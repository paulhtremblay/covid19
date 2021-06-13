import sys
import os
from google.cloud import storage
import google
import urllib.request
import tempfile
import csv
import datetime
import json

def get_github_state(url, verbose = False):
    if verbose:
        print('fetching {u}'.format(u = url))
    fh, path = tempfile.mkstemp()
    urllib.request.urlretrieve(url, path)
    return fh, path

def upload_to_storage(local_path, bucket_name, blob_name, 
        verbose = False):
    with open(local_path, 'rb') as fh:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_file(fh)
    if verbose:
        print('loaded {f} to {b}/{n}'.format(
            f = local_path, b = bucket_name, n = blob_name)
            )


def main(event, context):
    fh, path = get_github_state(
            url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv',
            verbose = True)
    upload_to_storage(local_path = path, 
        bucket_name = 'paul-henry-tremblay-covid19-2', 
        blob_name = 'covid_19_us_states.csv'
        )
    os.close(fh)
    os.remove(path)

