import sys
import os
import datetime
import shutil
import test_data
sys.path.append('..')
import unittest
from unittest import mock

from henry_covid19.mock_query_job import MockQeryJob
import by_state
from test_data import state_deaths
import copy

def mocked_client1(*args, **kwargs):

    class MockClient:

        def __init__(self):
            pass

        def dataset(self, datset_name):
            return Table()

        def query(self, sql,  job_config = None):
            if '/* STATE DEATHS */' in sql:
                d = state_deaths.d
            else:
                raise ValueError('no sql match')
            return MockQeryJob(d)
    return MockClient()

class TestMakeCountries(unittest.TestCase):

    def setUp(self):
        return
        if os.path.isdir('html_temp'):
            shutil.rmtree('html_temp')

    def tearDown(self):
        return
        if os.path.isdir('html_temp'):
            shutil.rmtree('html_temp')

    """
    @mock.patch('google.cloud.bigquery.Client', side_effect=mocked_client1)
    def test_main(self, bq):
        by_state.make_state_graphs()
    """
   
if __name__ == '__main__':
    unittest.main()
