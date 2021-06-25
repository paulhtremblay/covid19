import sys
import os
from google.cloud import storage
import google
import urllib.request
import tempfile
import csv
import datetime
import json

def get_hospitalizations():
    url = 'https://csom-mili-api-covidhospitalizations.s3.us-east-2.amazonaws.com/hospitalizations/hospitalizations.csv'
    fh_in, in_path = tempfile.mkstemp()
    fh_out, out_path = tempfile.mkstemp()
    urllib.request.urlretrieve(url, in_path)
    with open(out_path, 'w') as write_obj, open(in_path, 'r') as read_obj:
        fieldnames  = ['fips', 
            'state_abbreviation', 
            'state_name', 
            'date', 
            'state_reported_date', 
            'total_hosp_to_date', 
            'total_in_icu_to_date', 
            'current_hospitalizations', 
            'currently_in_icu', 
            'currently_on_ventilator', 
            'total_deaths']
        reader = csv.DictReader(read_obj)
        writer = csv.DictWriter(write_obj, fieldnames = fieldnames)
        read_fieldnames = reader.fieldnames
        d = {'FIPS': 'fips', 
            'StateAbbreviation': 'state_abbreviation', 
            'StateName':'state_name', 
            'Date':'date', 
            'StateReportedDate':'state_reported_date', 
            'TotalHospToDate':'total_hosp_to_date', 
            'TotalInICUToDate':'total_in_icu_to_date', 
            'CurrentHospitalizations':'current_hospitalizations', 
            'CurrentlyInICU':'currently_in_icu', 
            'CurrentlyOnVentilator':'currently_on_ventilator', 
            'TotalDeaths':'total_deaths'}
        writer.writeheader()
        for row in reader:
            row_dict = {}
            for i in read_fieldnames:
                v = row[i]
                if v == '' and i not in ['FIPS', 'StateAbbreviation', 'StateName', 'Date', 
                        'StateReportedDate']:
                    v = 0
                elif v == '' and i  in ['StateReportedDate']:
                    v = '1900-01-01'
                elif v == '' and i  in ['FIPS', 'StateAbbreviation', 'StateName',  
                        ]:
                    v = ''
                k = d[i]
                row_dict[k] = v
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
    fh, path = get_hospitalizations()
    upload_to_storage(local_path = path, 
        bucket_name = 'paul-henry-tremblay-covid19-2', 
        blob_name = 'covid19_hosptials.csv'
        )

    os.close(fh)
    os.remove(path)

if __name__ == '__main__':
    main(None, None)
