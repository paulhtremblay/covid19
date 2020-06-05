import os
import pprint
pp = pprint.PrettyPrinter(indent = 4)
import csv
import pandas as pd

from jinja2 import Environment, select_autoescape, FileSystemLoader

from henry_covid19 import common
from henry_covid19 import variables
from henry_covid19 import bootstrap

ENV = Environment(
    loader=FileSystemLoader([
          os.path.join(os.path.split(os.path.abspath(__file__))[0], 'templates'),
          os.path.join(os.path.split(os.path.abspath(__file__))[0], 'includes'),
    ]),
    autoescape=select_autoescape(['html', 'xml'])
)

def get_territory_list(territory_key ='state'):
    if territory_key == 'state':
        csv_file_name = 'states'
    else:
        csv_file_name = 'world'
    csv_file_name += '.csv'

    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), csv_file_name)
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)

    if territory_key == 'state':
        territory_list = df.state.unique()
    else:
        territory_list = df.country.unique()

    return territory_list




def make_nav():
    """
    create nav list of US states
    """

    state_list = get_territory_list('state')
    state_list = sorted(state_list)

    country_list = get_territory_list('country')
    country_list = sorted(country_list)

    t = ENV.get_template('nav.j2')
    t =  t.render(
            countries = [(common.make_hyphenated(x), x) for x in country_list],
            states = [(common.make_hyphenated(x), x) for x in state_list]
            )
    if not os.path.isdir('includes'):
        os.mkdir('includes')

    with open(os.path.join('includes', 'nav.html'), 'w') as write_obj:
        write_obj.write(t)


if __name__ == '__main__':
    make_nav()
