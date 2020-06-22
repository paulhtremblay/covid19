import datetime
import os
import datetime
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

ENV.filters['slugify'] = slugify

def get_territory_list(territory_key = 'country'):
    """
    Searches .csv file and returns unique regions from region column. Creates
    list of tuples, where the first field is the name of the web page, and the
    second is the page's url.
    :param territory_key: str determining which .csv file to search and filter
    :return: alphabetically sorted list of tuples
    """
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

    territory_list = sorted(territory_list)
    return territory_list

def get_site_updated_time():
    """
    bodge to make sure there's a date field
    TODO: add function in get_data.py to write a csv file with last_updated
    :return:
    """
    if not os.path.isdir('includes'):
        os.mkdir('includes')
    if not os.path.isfile('site_updated_time.txt'):
        site_updated_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(os.path.join('includes', 'site_updated_time.txt'), 'w') as write_obj:
            write_obj.write(site_updated_time)

def get_site_last_updated():
    """
    get last updated time stamp
    """
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'site_last_updated.csv')
    with open(path, 'r') as read_obj:
        lines = read_obj.readlines()
    d = datetime.datetime.strptime(lines[1][0:19], '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d %H:%M:%S")
    return d

    print(lines)
    
def make_nav():
    """
    create nav list of US states
    """

    get_site_updated_time()

    country_list = get_territory_list('country')
    state_list = get_territory_list('state')
    county_list = get_territory_list('county')

    t = ENV.get_template('nav.j2')
    t =  t.render(
            countries = country_list,
            states = state_list,
            counties = county_list
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
