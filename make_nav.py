import os
import pprint
pp = pprint.PrettyPrinter(indent = 4)
import csv
import pandas as pd

from jinja2 import Environment, select_autoescape, FileSystemLoader

from henry_covid19 import common
from henry_covid19 import variables
from henry_covid19 import bootstrap

from slugify import slugify

ENV = Environment(
    loader=FileSystemLoader([
          os.path.join(os.path.split(os.path.abspath(__file__))[0], 'templates'),
          os.path.join(os.path.split(os.path.abspath(__file__))[0], 'includes'),
    ]),
    autoescape=select_autoescape(['html', 'xml'])
)

def get_territory_list(territory_key ='country'):
    if territory_key == 'country':
        csv_file_name = 'world'
    elif territory_key == 'state':
        csv_file_name = 'states'
    else:
        csv_file_name = 'seven_day_county'
    csv_file_name += '.csv'

    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), csv_file_name)
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)

    if territory_key == 'country':
        territory_list = df.country.unique()
        territory_list = [w.replace('_', ' ') for w in territory_list]
    elif territory_key == 'state':
        territory_list = df.state.unique()
    else:
        territory_list = df.state.unique()

    return territory_list


def get_site_last_updated():
    """
    get last updated time stamp
    """
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'site_last_updated.csv')
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)
    return df.loc['site_last_updated'].iloc[0]




def make_nav():
    """
    create nav list of US states
    """

    country_list = get_territory_list('country')
    country_list = sorted(country_list)

    state_list = get_territory_list('state')
    state_list = sorted(state_list)

    county_list = get_territory_list('county')
    county_list = sorted(county_list)

    t = ENV.get_template('nav.j2')
    t =  t.render(

            countries = [(slugify(x), x) for x in country_list],
            states = [(slugify(x), x) for x in state_list],
            counties = [(slugify(x), x) for x in county_list]
            )
    if not os.path.isdir('includes'):
        os.mkdir('includes')

    with open(os.path.join('includes', 'nav.html'), 'w') as write_obj:
        write_obj.write(t)

    site_last_updated = get_site_last_updated()
    with open(os.path.join('includes', 'site_updated_time.txt'), 'w') as write_obj:
        write_obj.write(site_last_updated)



if __name__ == '__main__':
    make_nav()
