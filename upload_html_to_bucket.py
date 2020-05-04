import datetime
from google.cloud import storage
import os
import glob

def upload_to_storage(local_path, bucket_name, blob_name):
    with open(local_path, 'rb') as fh:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_file(fh, content_type = 'text/html')
        blob.cache_control = 'public, max-age=60'
        blob.patch()

def upload_to_storage_(s, bucket_name, blob_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(s, content_type = 'text/html')
    metadata = {'Cache-control': 'public, max-age=60', 'Content-Type':'text/html'}
    #blob.metadata = metadata
    #blob.patch()

def upload_html(bucket_name = 'www.paulhtremblay.com'):
    files = glob.glob('html_temp/*.html')
    for i in files:
        head, tail = os.path.split(i)
        upload_to_storage(local_path = i, bucket_name = bucket_name,
                blob_name = tail)

if __name__ == '__main__':
    upload_html()
