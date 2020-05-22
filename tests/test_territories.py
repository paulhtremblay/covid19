import sys
import os
import datetime
import shutil
#sys.path.append('/home/henry/projects/covid19')
import test_data
sys.path.append('..')
import unittest
from unittest import mock

import make_territories
import copy

def get_path_mock1(*args, **kwargs):
    return os.path.join('test_data', args[1])

class TestMakeCountries(unittest.TestCase):

    def setUp(self):
        if os.path.isdir('html_temp'):
            shutil.rmtree('html_temp')

    def tearDown(self):
        if os.path.isdir('html_temp'):
            shutil.rmtree('html_temp')

    @mock.patch('henry_covid19.common.get_data_path', side_effect=get_path_mock1)
    def test_main(self, bq):
        make_territories.main()
        self.assertTrue(len(os.listdir('html_temp')) > 0)
        self.assertTrue('countries' in os.listdir('html_temp'))
   
if __name__ == '__main__':
    unittest.main()
