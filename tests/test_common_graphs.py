import datetime
import sys
sys.path.append('..')
import unittest
from henry_covid19 import common
from bokeh.io import show


class TestGraphs(unittest.TestCase):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_graph_stacked(self):
        date = datetime.datetime(2020, 1, 1)
        reg1 = 1
        reg2 = 3
        d = {'dates': [],
                'region1':[],
                'region2':[],
                }
        for i in range(15):
            date +=  datetime.timedelta(days = 1)
            d['dates'].append(date)
            reg1 += 1
            reg2 += 2
            d['region1'].append(reg1)
            d['region2'].append(reg2)
        p =  common.graph_stacked(data = d, start = 1, plot_height = 450,line_width = 10)

    def test_graph_stacked_date(self):
        date = datetime.datetime(2020, 1, 1)
        reg1 = 1
        reg2 = 3
        d = {'dates': [],
                'region1':[],
                'region2':[],
                }
        for i in range(15):
            date +=  datetime.timedelta(days = 1)
            d['dates'].append(date)
            reg1 += 1
            reg2 += 2
            d['region1'].append(reg1)
            d['region2'].append(reg2)
        d['dates'] = [x.date() for x in d['dates']]
        p =  common.graph_stacked(data = d, start = 1, plot_height = 450, 
                line_width = 10, colors = ['Crimson', 'LightGreen', 'Salmon'])
        #show(p)

   
if __name__ == '__main__':
    unittest.main()
