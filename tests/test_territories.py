import sys
import os
import datetime
import shutil
#sys.path.append('/home/henry/projects/covid19')
import test_data
sys.path.append('..')
import unittest
from unittest import mock

from henry_covid19.mock_query_job import MockQeryJob
import make_territories
from test_data import world_by_week_short
from test_data import world_by_day_short
from test_data import country
import copy

def mocked_client1(*args, **kwargs):

    class MockClient:

        def __init__(self):
            pass

        def dataset(self, datset_name):
            return Table()

        def query(self, sql,  job_config = None):

            if '/* WORLD BY WEEK */' in sql:
                d = test_data.world_by_week_short.d
            elif '/* WORLD BY DAY */' in sql:
                d = test_data.world_by_day_short.d
            elif '/* STATE BY WEEK */' in sql:
                d = copy.deepcopy(test_data.world_by_week_short.d)
                d['state'] =  d['country']
            elif '/* STATE BY DAY */' in sql:
                d = copy.deepcopy(test_data.world_by_day_short.d)
                d['state'] =  d['country']
            else:
                raise ValueError('no sql match')
            return MockQeryJob(d)
    return MockClient()

class TestMakeCountries(unittest.TestCase):

    def setUp(self):
        if os.path.isdir('html_temp'):
            shutil.rmtree('html_temp')

    def tearDown(self):
        if os.path.isdir('html_temp'):
            shutil.rmtree('html_temp')


    @mock.patch('google.cloud.bigquery.Client', side_effect=mocked_client1)
    def test_main(self, bq):
        make_territories.main()
        self.assertTrue(len(os.listdir('html_temp')) > 0)
        self.assertTrue('states' in os.listdir('html_temp'))
        self.assertTrue('countries' in os.listdir('html_temp'))
   
if __name__ == '__main__':
    unittest.main()
