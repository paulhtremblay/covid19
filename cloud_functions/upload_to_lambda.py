import sys
import os
from google.cloud import storage
import google
import urllib.request
import tempfile
import csv
import datetime
import json

def main(path):
    bucket_name = 'paulhtremblay-lambda-source'
    with open(path, 'rb') as fh:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(path)
        blob.upload_from_file(fh)


if __name__ == '__main__':
    main(sys.argv[1])
