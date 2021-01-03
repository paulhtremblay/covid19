import sys
import os
from google.cloud import storage
import google
from google.cloud import bigquery
import urllib.request
import tempfile
import csv
import datetime
import json

def get_world_data2():
    path = 'world2.csv'
    path2 = 'world3.csv'
    with open(path2, 'w') as write_obj, open(path, 'r') as read_obj:
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
    return path2

def get_world_data2_():
    path = 'world2.csv'
    path2 = 'world3.csv'
    with  open(path, 'w') as write_obj:
        url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
        urllib.request.urlretrieve(url, path)

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

    #note that totalTestEncountersViral is not deprecated, but it was added late, so ignoring
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
    'deathConfirmed': True,
    'deathProbable': True,

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

    allowed_fields = {
            'date':True,
            'state':True,
            'fips': True,
            }

    allowed_fields_ = {
            'date':True,
            'state':True,
            'fips': True,
            'totalTestEncountersViral': True,
            'totalTestsPeopleViral': True,
            'totalTestsAntibody':True,
            'positiveTestsAntibody': True,
            'negativeTestsAntibody': True,
            'totalTestsPeopleAntibody':True,
            'positiveTestsPeopleAntibody': True,
            'negativeTestsPeopleAntibody':True,
            'totalTestsPeopleAntigen': True,
            'positiveTestsPeopleAntigen':True,
            'totalTestsAntigen':True,
            'positiveTestsAntigen':True,
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
    bad_found = {}
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
                        true_name = good_fields.get(i)
                        if not true_name and not int_dict.get(i) and not allowed_fields.get(i):
                            if not bad_found.get(i):
                                sys.stderr.write('{i} will be ignored\n'.format(i = i))
                            bad_found[i] = True
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
                        elif int_dict.get(true_name) and (row[i] == '' or row[i] == 'NaN'):
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
            else:
                deaths = row[5]
                if deaths == '':
                    deaths = 0
                if row[1] == 'New York City' and row[2] == 'New York':
                    csv_writer.writerow([row[0], row[1], row[2], '36061', row[4], deaths])
                else:
                    csv_writer.writerow([row[0], row[1], row[2], row[3], row[4], deaths])
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
    client = bigquery.Client()
    cron_d = '/home/henry/cron_logs/'
    if verbose:
        print('uploading to storage')
    upload_to_storage(local_path =  '/home/henry/projects/covid19-infection-estimates-latest/latest_all_estimates_us.csv',
            bucket_name = 'paul-henry-tremblay-covid19', 
            blob_name = 'covid19_infections_estimates.csv'
            )
    upload_to_bq(client = client, 
        gs_path = 'gs://paul-henry-tremblay-covid19/covid19_infections_estimates.csv',
        table_name = 'infection_estimates'
        )
    local_path = get_world_data2()
    upload_to_storage(local_path = local_path, 
            bucket_name = 'paul-henry-tremblay-covid19', 
            blob_name = 'covid19_world2.csv'
            )
    upload_to_bq(client = client, 
        gs_path = 'gs://paul-henry-tremblay-covid19/covid19_world2.csv',
        table_name = 'world2'
        )
    with open(os.path.join(cron_d, 'upload.txt'), 'a') as write_obj:
        write_obj.write('Starting load job at {d}\n'.format(d = datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')))
    with open(os.path.join(cron_d, 'upload.txt'), 'a') as write_obj:
        write_obj.write('client loaded at {d}\n'.format(d = datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')))
    fix_us_counties('us-counties.csv')
    with open(os.path.join(cron_d, 'upload.txt'), 'a') as write_obj:
        write_obj.write('fixed at {d}\n'.format(d = datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')))
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
    
    """
    path = get_html_file('https://opendata.ecdc.europa.eu/covid19/casedistribution/csv')
    upload_to_storage(local_path = path, 
            bucket_name = 'paul-henry-tremblay-covid19', 
            blob_name = 'covid_19_world.csv'
            )
    upload_to_bq(client = client, 
        gs_path = 'gs://paul-henry-tremblay-covid19/covid_19_world.csv',
        table_name = 'world'
        )
    """
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
    with open('/home/henry/cron_logs/upload.txt', 'a') as write_obj:
        write_obj.write('successfully uploaded at {d}\n'.format(
            d = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
