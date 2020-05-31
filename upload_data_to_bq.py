import os
from google.cloud import storage
import google
from google.cloud import bigquery
import urllib.request
import tempfile
import csv
import datetime

def get_html_file(url):
    fh, path = tempfile.mkstemp()
    urllib.request.urlretrieve(url, path)
    with open(path, 'r') as read_obj, open('world_tmp.csv', 'w') as write_obj:
        reader = csv.DictReader(read_obj)
        csv_writer = csv.writer(write_obj)
        counter = 0
        for row in reader:
            counter += 1
            if counter == 1:
                continue
            date = datetime.datetime.strptime(row['dateRep'], '%d/%m/%Y').strftime('%Y-%m-%d')
            country = row['countriesAndTerritories']
            country_code1 = row['geoId']
            country_code2 = row['countryterritoryCode']
            if not country_code2:
                country_code2 = 'N/A'
            cases = row['cases']
            deaths = row['deaths']
            population = row['popData2018']
            if population == '':
                population = 0
            csv_writer.writerow([date, country, country_code1, country_code2, cases, deaths, population])
    os.close(fh)
    os.remove(path)
    return 'world_tmp.csv'

def upload_to_storage(local_path, bucket_name, blob_name):
    with open(local_path, 'rb') as fh:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_file(fh)

def fix_us_counties(path):
    # new york city no fips
    #date,county,state,fips,cases,deaths
    out_path = 'us_counties_tmp.csv'
    with open(path, 'r') as read_obj, open(out_path, 'w') as write_obj:
        csv_reader = csv.reader(read_obj)
        csv_writer = csv.writer(write_obj)
        counter = 0
        for row in csv_reader:
            counter += 1
            if counter == 1:
                csv_writer.writerow(row)
            elif row[1] == 'New York City' and row[2] == 'New York':
                csv_writer.writerow([row[0], row[1], row[2], '36061', row[4], row[5]])
            else:
                csv_writer.writerow(row)
    return out_path


def upload_to_bq(client, gs_path, table_name):
    if not client:
        client = bigquery.Client()
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    #job_config.field_delimiter = '\t'
    job_config.write_disposition = 'WRITE_TRUNCATE'
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




def main(verbose = False):
    if verbose:
        print('uploading to storage')
    client = bigquery.Client()
    fix_us_counties('us-counties.csv')
    upload_to_storage(local_path = 'us-states.csv', 
            bucket_name = 'paul-henry-tremblay-covid19', 
            blob_name = 'covid_19_us_states.csv'
            )
    upload_to_storage(local_path = 'us_counties_tmp.csv', 
            bucket_name = 'paul-henry-tremblay-covid19', 
            blob_name = 'covid_19_us_counties.csv'
            )
    upload_to_bq(client = client, 
        gs_path = 'gs://paul-henry-tremblay-covid19/covid_19_us_states.csv',
        table_name = 'us_states'
        )
    upload_to_bq(client = client, 
        gs_path = 'gs://paul-henry-tremblay-covid19/covid_19_us_counties.csv',
        table_name = 'us_counties'
        )
    
    path = get_html_file('https://opendata.ecdc.europa.eu/covid19/casedistribution/csv')
    upload_to_storage(local_path = path, 
            bucket_name = 'paul-henry-tremblay-covid19', 
            blob_name = 'covid_19_world.csv'
            )
    upload_to_bq(client = client, 
        gs_path = 'gs://paul-henry-tremblay-covid19/covid_19_world.csv',
        table_name = 'world'
        )
    
    


if __name__ == '__main__':
    main()
