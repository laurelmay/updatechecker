import json
import os

import boto3
import requests

from botocore.exceptions import ClientError

from checkers.eclipse_java import EclipseJavaChecker
from checkers.jgrasp import JGraspChecker
from checkers.finch_py import FinchChecker
from checker import BaseUpdateCheckerEncoder


_S3_PREFIX = os.environ.get('S3_PREFIX', 'updatechecker').rstrip('/')

s3 = boto3.client('s3')
sns = boto3.client('sns')


def s3_key(software):
    return f"{_S3_PREFIX}/{software}.json"


def load_data(s3, bucket, key):
    body = s3.get_object(
        Bucket=bucket,
        Key=key,
    )['Body']
    return json.load(body)


def remap_data(data):
    remapped = {}
    for entry in data:
        remapped[entry['software']] = entry['latest']
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
    sns.publish(
        TopicArn=topic,
        Subject=subject,
        Message=message
    )


def notify_failure(name, err, topic):
    print(f"Notifying of failure for {name}")
    subject = f"Failed to check updates for {name}"
    message = f"""
    Error details:
    {err}
    """
    sns.publish(
        TopicArn=topic,
        Subject=subject,
        Message=message
    )


def handler(event, context):
    bucket = os.environ['bucket']
    email_topic = os.environ['email_topic']
    beta = os.environ.get('beta', False)
    force_notify = event.get('force-notify', False)

    session = requests.Session()
    session.headers.update({'User-Agent': 'Update Check tool'})
    context = {
        'eclipse': {
            'mirror_url': 'http://mirror.math.princeton.edu/pub/eclipse/technology/epp/downloads/release',
        },
    }
    notifications = []
    for chk in [EclipseJavaChecker, JGraspChecker, FinchChecker]:
        try:
            checker_instance = chk(context, session, beta)
            new_json = json.dumps(checker_instance, indent=4, cls=BaseUpdateCheckerEncoder)
        except Exception as exc:
            notify_failure(chk.name, exc, email_topic)
            continue

        new_data = json.loads(new_json)['latest']
        try:
            old_data = load_data(s3, bucket, s3_key(chk.short_name))
        except:
            old_data = []

        # There's not even a need to re-write the data if there is not a new version
        # of any of the software.
        if new_data == old_data and not force_notify:
            continue

        print(f"Old: {json.dumps(old_data)}")
        print(f"New: {json.dumps(new_data)}")

        notify(chk.name, new_data, email_topic)
        notifications.append(chk.name)
        try:
            s3.put_object(Bucket=bucket, Key=s3_key(chk.short_name), Body=json.dumps(new_data))
        except ClientError as err:
            notify_failure(chk.name, f"Unable to write to S3: {err}", email_topic)

    return {'notifications': notifications}
