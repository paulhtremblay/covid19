import sys
import os
from google.cloud import storage
import google
import urllib.request
import tempfile
import csv
import datetime
import json

def get_world_data():
    fh_in, in_path= tempfile.mkstemp() 
    fh_out, out_path= tempfile.mkstemp() 
    url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
    urllib.request.urlretrieve(url, in_path)
    with open(out_path, 'w') as write_obj, open(in_path, 'r') as read_obj:
        reader = csv.DictReader(read_obj)
        writer = csv.writer(write_obj)
        fieldnames = reader.fieldnames
        for row in reader:
            date = row['date']
            new_cases = row['new_cases']
            if row['new_cases'] == '':
                new_cases = 0
            else:
                new_cases = int(float(row['new_cases']))
            if row['new_deaths'] == '':
                new_deaths = 0
            else:
                new_deaths = int(float(row['new_deaths']))
            if row['population'] == '':
                population = 0
            else:
                try:
                    population = int(row['population'])
                except ValueError:
                    population = int(float(row['population']))
            iso_code = row['iso_code']
            country = row['location']
            if row['total_cases'] == '':
                total_cases = 0
            else:
                total_cases = int(float(row['total_cases']))
            if row['total_deaths'] == '':
                total_deaths = 0
            else:
                total_deaths = int(float(row['total_deaths']))
            if row['icu_patients'] == '':
                icu_patients = 0
            else:
                icu_patients = int(float(row['icu_patients']))
            if row['hosp_patients'] == '':
                hosp_patients = 0
            else:
                hosp_patients = int(float(row['hosp_patients']))
            if iso_code == '':
                continue
            new_row = [date, iso_code, country, total_cases, total_deaths,
                    new_cases, new_deaths, hosp_patients, icu_patients, population]
            writer.writerow(new_row)
    return fh_out, out_path


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
    fh, path = get_world_data()
    upload_to_storage(local_path = path, 
        bucket_name = 'paul-henry-tremblay-covid19-2', 
        blob_name = 'covid19_world.csv'
        )

    os.close(fh)
    os.remove(path)



