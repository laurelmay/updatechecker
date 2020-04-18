import json
import os

import boto3
import requests

from botocore.exceptions import ClientError

from checkers.eclipse_java import EclipseJavaChecker
from checkers.jgrasp import JGraspChecker
from checkers.finch_py import FinchChecker
from checker import BaseUpdateCheckerEncoder


_S3_KEY = 'version-data.json'

s3 = boto3.client('s3')
sns = boto3.client('sns')


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
    message = f"""
    A new version of {name} is available.

        Version: {data['version']}
        URL: {data['url']}
        SHA1: {data['sha1']}
        Beta: {data['beta']}
    """
    sns.publish(
        TopicArn=topic,
        Message=message
    )


def handler(event, context):
    bucket = os.environ['bucket']
    email_topic = os.environ['email_topic']
    beta = os.environ.get('beta', False)

    session = requests.Session()
    session.headers.update({'User-Agent': 'Update Check tool'})
    context = {
        'eclipse': {
            'mirror_url': 'http://mirror.math.princeton.edu/pub/eclipse/technology/epp/downloads/release',
        },
    }
    eclipse = EclipseJavaChecker(context, session, beta)
    jgrasp = JGraspChecker(context, session, beta)
    finch = FinchChecker(context, session, beta)

    new_json = json.dumps([eclipse, jgrasp, finch], indent=4, cls=BaseUpdateCheckerEncoder)
    new_data = json.loads(new_json)

    try:
        old_data = load_data(s3, bucket, _S3_KEY)
    except:
        old_data = []

    # There's not even a need to re-write the data if there is not a new version
    # of any of the software.
    if new_data == old_data:
        return {
            'notifications': 0,
            's3_write': False
        }

    print(f"Old: {json.dumps(old_data)}")
    print(f"New: {json.dumps(new_data)}")

    new_remap = remap_data(new_data)
    old_remap = remap_data(old_data)

    notifications = 0

    for name, data in new_remap.items():
        if name not in old_remap or data != old_remap[name]:
            notify(name, data, email_topic)
            notifications += 1
    
    try:
        s3.put_object(Bucket=bucket, Key=_S3_KEY, Body=new_json)
    except ClientError as err:
        print(err)
        return {
            'notifications': notifications,
            's3_write': False
        }
    else:
        return {
            'notifications': notifications,
            's3_write': True
        }
