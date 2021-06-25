import sys
import os
from google.cloud import storage
import google
import urllib.request
import tempfile
import csv
import datetime
import json



def get_vaccines():
    url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv'
    fh_in, in_path = tempfile.mkstemp()
    fh_out, out_path = tempfile.mkstemp()
    urllib.request.urlretrieve(url, in_path)
    with open(out_path, 'w') as write_obj, open(in_path, 'r') as read_obj:
        fieldnames= ['date', 'location', 'total_vaccinations', 
                'total_distributed', 'people_vaccinated', 'people_fully_vaccinated_per_hundred', 
                'total_vaccinations_per_hundred', 'people_fully_vaccinated', 
                'people_vaccinated_per_hundred', 'distributed_per_hundred', 
                'daily_vaccinations_raw', 'daily_vaccinations', 
                'daily_vaccinations_per_million', 'share_doses_used']
        reader = csv.DictReader(read_obj)
        writer = csv.DictWriter(write_obj, fieldnames = fieldnames)
        writer.writeheader()
        row_dict = {}
        for row in reader:
            for key in row.keys():
                if key == 'date':
                    value = datetime.datetime.strptime(row[key], '%Y-%m-%d')
                elif key == 'location':
                    value = row[key]
                elif row[key] == '':
                    value = 0
                else:
                    value = float(row[key])
                row_dict[key] = value
            writer.writerow(row_dict)
    os.close(fh_in)
    os.remove(in_path)
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
    fh, path = get_vaccines()
    upload_to_storage(local_path = path, 
        bucket_name = 'paul-henry-tremblay-covid19-2', 
        blob_name = 'covid19_vaccines.csv'
        )

    os.close(fh)
    os.remove(path)

if __name__ == '__main__':
    main(None, None)
