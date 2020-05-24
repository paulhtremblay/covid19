import datetime
import sys
sys.path.append('..')
import unittest
from henry_covid19 import bootstrap


class TestBootstrap(unittest.TestCase):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_bootstrap(self):
        sample1 = [1, 2, 3, 5]
        sample2 = [1, 2, 3, 5]
        r = bootstrap.resample_two_samples(sample1, sample2)

    def test_combine(self):
        sample1 = [1, 2, 3, 5]
        sample2 = [1, 2, 3, 5]
        r1, r2 = bootstrap.resample_two_samples(sample1, sample2)
        bootstrap.combine_resamples(sample1, sample2, r1, r2)

    def test_pvalue(self):
        sample1 = [1, 2, 3, 5]
        sample2 = [1, 2, 3, 5]
        r1, r2 = bootstrap.resample_two_samples(sample1, sample2)
        b = bootstrap.combine_resamples(sample1, sample2, r1, r2)
        bootstrap.get_p_value(b)
   
if __name__ == '__main__':
    unittest.main()
