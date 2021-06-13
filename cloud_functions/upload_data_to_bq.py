import sys
import os
import google
from google.cloud import bigquery
import urllib.request
import tempfile
import csv
import datetime
import json

def upload_to_bq(gs_path, table_name, source_format ='csv'):
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig()
    if source_format == 'csv':
        job_config.source_format = bigquery.SourceFormat.CSV
    elif source_format == 'json':
        job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    job_config.write_disposition = 'WRITE_TRUNCATE'
    if source_format == 'csv':
        job_config.skip_leading_rows = 1
    dataset_ref = client.dataset('covid19')
    dataset = bigquery.Dataset(dataset_ref)
    load_job = client.load_table_from_uri(
           gs_path, dataset_ref.table(table_name),
          job_config=job_config)
    try:
        load_job.result()
    except google.api_core.exceptions.BadRequest:
        raise ValueError(load_job.errors)

def main(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    d = {'covid_19_us_states.csv':'us_states'
            }
    
    file_path = event['name']
    assert d.get(file_path), 'File path {f} has no matching table'.format(
            f = file_path)
    upload_to_bq(gs_path = 'gs://paul-henry-tremblay-covid19/{f}'.format(f = file_path),
        table_name = d[file_path]
        )

if __name__ == '__main__':
    main()
