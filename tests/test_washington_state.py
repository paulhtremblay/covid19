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
import washington_state
from test_data import us_states_short
from test_data import wa_weekly_county
import copy

def mocked_client1(*args, **kwargs):

    class MockClient:

        def __init__(self):
            pass

        def dataset(self, datset_name):
            return Table()

        def query(self, sql,  job_config = None):
            if 'US STATES' in sql:
                d = test_data.us_states_short.d
            elif '* WA COUNTIES *' in sql:
                d = test_data.wa_weekly_county.d
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
        washington_state.make_washington_graphs()
        self.assertTrue(len(os.listdir('html_temp')) > 0)
   
if __name__ == '__main__':
    unittest.main()
