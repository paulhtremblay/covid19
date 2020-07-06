import os
from google.cloud import storage
import google
from google.cloud import bigquery
import urllib.request
import tempfile
import csv
import datetime
import json

def covid_tracker_get():
    state_abb = {'al': True, 'ak': True, 'az': True, 'ar': True, 'ca': True, 
            'co': True, 'ct': True, 'de': True, 'dc': True, 
            'fl': True, 'ga': True, 'hi': True, 'id': True, 'il': True, 
            'in': True, 'ia': True, 'ks': True, 'ky': True, 
            'la': True, 'me': True, 'md': True, 'ma': True, 'mi': True, 
            'mn': True, 'ms': True, 'mo': True, 'mt': True, 
            'ne': True, 'nv': True, 'nh': True, 'nj': True, 'nm': True, 
            'ny': True, 'nc': True, 'nd': True, 'oh': True, 'ok': True, 
            'or': True, 'pa': True, 'ri': True, 'sc': True, 'sd': True, 
            'tn': True, 'tx': True, 'ut': True, 'vt': True, 'va': True, 
            'wa': True, 'wv': True, 'wi': True, 'wy': True}

    deprecated = {'checkTimeEt': True,
    'commercialScore' : True,
    'dateChecked' : True,
    'dateModified' : True,
    'grade' : True,
    'hospitalized' : True,
    'negativeIncrease' : True,
    'negativeRegularScore' : True,
    'negativeScore' : True,
    'hash' : True,
    'posNeg' : True,
    'score' : True,
    'positiveScore' : True,
    'total' : True,
            }

    good_fields = {
            'hospitalizedCurrently': 'hospitalized_currently',
            'hospitalizedCumulative' : 'hospitalized_cumulative',
            'inIcuCurrently':'in_icu_currently',
            'onVentilatorCurrently': 'on_ventilator_currently',
            'dataQualityGrade':'data_quality_grade',
            'lastUpdateEt':'last_update_et',
            'totalTestsViral':'total_tests_viral',
            'positive_tests_viral':'positive_tests_viral',
            'negativeTestsViral':'negative_tests_viral',
            'positiveCasesViral':'positive_cases_viral',
            'totalTestResults':'total_test_results',
            'totalTestResultsIncrease':'total_test_results_increase',
            'deathIncrease':'death_increase',
            'hospitalizedIncrease':'hospitalized_increase',
            'onVentilatorCumulative':'on_ventilator_cumulative',
            'positiveTestsViral':'positive_tests_viral',
            'positiveIncrease':'positive_increase',
            'inIcuCumulative':'in_icu_cumulative',
            }

    int_dict = {'positive':True,
            'negative':True,
            'pending':True,
            "hospitalized_currently": True, 
            "hospitalized_cumulative": True, 
            "in_icu_currently": True, 
            "in_icu_cumulative": True, 
            "on_ventilator_currently": True, 
            "on_ventilator_cumulative": True, 
            "recovered": True, 
            "death": True, 
            "total_tests_viral": True, 
            "positive_tests_viral": True, 
            "negative_tests_viral": True, 
            "positive_cases_viral": True, 
            "positive_increase": True, 
            "total_test_results": True, 
            "total_test_results_increase": True, 
            "death_increase": True, 
            "hospitalized_increase": True}
    fh, path = tempfile.mkstemp()
    fh2, path2 = tempfile.mkstemp()
    out_path = 'covid_tracker_states.json'
    with  open(out_path, 'w') as write_obj:
        for j in state_abb.keys():
            url = 'https://covidtracking.com/api/v1/states/{s}/daily.csv'.format(s = j)
            urllib.request.urlretrieve(url, path)
            with open(path, 'r') as read_obj:
                reader = csv.DictReader(read_obj)
                fieldnames = reader.fieldnames
                for row in reader:
                    new_d = {}
                    for i in fieldnames:
                        if deprecated.get(i):
                            continue
                        true_name = good_fields.get(i, i)
                        if true_name == 'date':
                            new_d['date'] = datetime.datetime.strptime(row[i], '%Y%m%d')\
                                    .strftime('%Y-%m-%d')
                        elif true_name == "last_update_et": 
                            try:
                                new_d['last_update_et'] = datetime.datetime.strptime(row[i], '%m/%d/%Y %H:%M%S')\
                                        .strftime('%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                new_d['last_update_et'] = ''
                        elif int_dict.get(true_name) and row[i] == '':
                            new_d[true_name] = 0
                        elif int_dict.get(true_name):
                            new_d[true_name] = int(row[i])
                        else:
                            new_d[true_name] = row[i]
                    write_obj.write('{j}\n'.format(j = json.dumps(new_d)))
            os.remove(path)

def get_html_file(url):
    fh, path = tempfile.mkstemp()
    urllib.request.urlretrieve(url, path)
    fh2, path2 = tempfile.mkstemp()
    with open(path2, 'w') as write_obj, open(path, 'r') as read_obj:
        for line in read_obj.readlines():
            line = line.replace('\ufeff', '')
            write_obj.write(line)
    with open(path2, 'r') as read_obj, open('world_tmp.csv', 'w') as write_obj:
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
            population = row['popData2019']
            if population == '':
                population = 0
            csv_writer.writerow([date, country, country_code1, country_code2, cases, deaths, population])
    os.close(fh)
    os.remove(path)
    os.close(fh2)
    os.remove(path2)
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


def upload_to_bq_old(client, gs_path, table_name):
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


def upload_to_bq(client, gs_path, table_name, source_format ='csv'):
    if not client:
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
    covid_tracker_get()
    upload_to_storage(local_path = 'covid_tracker_states.json', 
            bucket_name = 'paul-henry-tremblay-covid19', 
            blob_name = 'covid19_proj_states.json'
            )
    upload_to_bq(client, 
            gs_path = 'gs://paul-henry-tremblay-covid19/covid19_proj_states.json', 
            table_name = 'covid19_track_states',
            source_format ='json')
    
if __name__ == '__main__':
    main()
