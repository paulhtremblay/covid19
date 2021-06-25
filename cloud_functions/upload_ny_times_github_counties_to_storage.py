import sys
import os
from google.cloud import storage
import google
import urllib.request
import tempfile
import csv
import datetime
import json

def fix_us_counties(path):
    # new york city no fips
    fh, out_path = tempfile.mkstemp()
    with open(path, 'r') as read_obj, open(out_path, 'w') as write_obj:
        csv_reader = csv.reader(read_obj)
        csv_writer = csv.writer(write_obj)
        counter = 0
        for row in csv_reader:
            counter += 1
            if counter == 1:
                csv_writer.writerow(row)
            else:
                deaths = row[5]
                if deaths == '':
                    deaths = 0
                if row[1] == 'New York City' and row[2] == 'New York':
                    csv_writer.writerow([row[0], row[1], row[2], '36061', row[4], deaths])
                else:
                    csv_writer.writerow([row[0], row[1], row[2], row[3], row[4], deaths])
    return fh, out_path

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
            url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv',
            verbose = True)
    fh2, path2 = fix_us_counties(path)
    os.close(fh)
    os.remove(path)
    upload_to_storage(local_path = path2, 
        bucket_name = 'paul-henry-tremblay-covid19-2', 
        blob_name = 'covid_19_us_counties.csv'
        )

    os.close(fh2)
    os.remove(path2)
