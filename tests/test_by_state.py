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
from test_data import state_cases
from test_data import us_states
import copy
from henry_covid19 import common


def mocked_client1(*args, **kwargs):

    class MockClient:

        def __init__(self):
            pass

        def dataset(self, datset_name):
            return Table()

        def query(self, sql,  job_config = None):
            if '/* STATE DEATHS */' in sql:
                d = state_deaths.d
            elif '/* STATE CASES */' in sql:
                d = state_cases.d
            elif '/* STATE BY DAY */' in sql:
                d = test_data.us_states.d
            else:
                raise ValueError('no sql match')
            return MockQeryJob(d)
    return MockClient()

def get_path_mock1(*args, **kwargs):
    return os.path.join('test_data', args[1])

class TestMakeCountries(unittest.TestCase):

    def setUp(self):
        return
        if os.path.isdir('html_temp'):
            shutil.rmtree('html_temp')

    def tearDown(self):
        return
        if os.path.isdir('html_temp'):
            shutil.rmtree('html_temp')

    @mock.patch('henry_covid19.common.get_data_path', side_effect=get_path_mock1)
    def test_main(self, bq):
        by_state.make_state_graphs(verbose = False)
   
if __name__ == '__main__':
    unittest.main()
