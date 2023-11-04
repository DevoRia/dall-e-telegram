from datetime import datetime

import boto3
import requests

session = None
s3_client = None


def set_s3_creds(access_key, secret_key):
    global session, s3_client
    session = boto3.Session(region_name='eu-north-1', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    s3_client = session.resource('s3')


def put_object(bucket_name, folder, name, url):
    r = requests.get(url, stream=True)

    file_name = f"{folder}/{name[:10]}{datetime.now()}.png"
    bucket = s3_client.Bucket(bucket_name)
    bucket.upload_fileobj(r.raw, file_name)
    return f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
