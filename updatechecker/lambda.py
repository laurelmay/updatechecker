import json
from json.decoder import JSONDecodeError
import os

import boto3
import requests

from botocore.exceptions import ClientError

from checkers.eclipse_java import EclipseJavaChecker
from checkers.jgrasp import JGraspChecker
from checkers.finch_py import FinchChecker
from checker import BaseUpdateCheckerEncoder


_S3_PREFIX = os.environ.get("S3_PREFIX", "updatechecker").rstrip("/")

s3 = boto3.client("s3")
sns = boto3.client("sns")


def s3_key(software):
    return f"{_S3_PREFIX}/{software}.json"


def load_stored_data(s3, bucket, key):
    body = s3.get_object(
        Bucket=bucket,
        Key=key,
    )["Body"]
    return json.load(body)


def remap_data(data):
    remapped = {}
    for entry in data:
        remapped[entry["software"]] = entry["latest"]
    return remapped


def notify(name, data, topic):
    print(f"Notifying for {name}.")
    subject = f"{name} update available"
    message = f"""
    A new version of {name} is available.

        Version: {data['version']}
        URL: {data['url']}
        SHA1: {data['sha1']}
        Beta: {data['beta']}
    """
    sns.publish(TopicArn=topic, Subject=subject, Message=message)


def notify_failure(name, err, topic):
    print(f"Notifying of failure for {name}")
    subject = f"Failed to check updates for {name}"
    message = f"""
    Error details:
    {err}
    """
    sns.publish(TopicArn=topic, Subject=subject, Message=message)


def configure_session():
    session = requests.Session()
    session.headers.update({"User-Agent": "Update checking tool"})
    return session


def get_latest_version_data(checker, context, session, beta=None):
    if beta is None:
        beta = os.environ.get("beta", False)
    checker_instance = checker(context, session, beta)
    version_data_json = json.dumps(checker_instance, cls=BaseUpdateCheckerEncoder)
    new_data = json.loads(version_data_json)["latest"]
    return new_data


def handler(event, context):
    bucket = os.environ["bucket"]
    email_topic = os.environ["email_topic"]
    beta = os.environ.get("beta", False)
    force_notify = event.get("force-notify", False)

    session = configure_session()
    context = {}
    notifications = []
    for chk in [EclipseJavaChecker, JGraspChecker, FinchChecker]:
        try:
            new_data = get_latest_version_data(chk, context, session, beta)
        except Exception as exc:
            notify_failure(chk.name, exc, email_topic)
            continue

        try:
            old_data = load_stored_data(s3, bucket, s3_key(chk.short_name))
        except (ClientError, JSONDecodeError):
            old_data = []

        # There's not even a need to re-write the data if there is not a new version
        # of any of the software.
        if new_data == old_data and not force_notify:
            continue

        notify(chk.name, new_data, email_topic)
        notifications.append(chk.name)
        try:
            s3.put_object(
                Bucket=bucket, Key=s3_key(chk.short_name), Body=json.dumps(new_data)
            )
        except ClientError as err:
            notify_failure(chk.name, f"Unable to write to S3: {err}", email_topic)

    return {"notifications": notifications}
