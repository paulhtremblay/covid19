#!/usr/bin/env python
# coding: utf-8

# In[10]:
"""Using Bokeh to plot the counties reopening status in WA"""
"""thresholds is a number which WA decides to reopen the county to  which phase,
    which currently is new confirmed cases per 100k people in 14 days span, equal or below 10."""

from google.cloud import bigquery
import datetime
from bokeh.io import show
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import gridplot
from bokeh.models import HoverTool  # show details when hovering the figure


def get_data():
    sql = """
    select
      c.date,
      c.state,
      c.county,
      ruc.FIPS,
      c.cases as accum_cases,-- In table covid19.us_counties,the cases and deaths are accumulated to date
      c.deaths as accum_deaths,-- In table covid19.us_counties,the cases and deaths are accumulated to date
      c.cases - lag(c.cases,14) over (partition by c.fips order by c.date) as two_weekly_cases,
            --using slq window function to sum two-weekly new cases on rolling bases
      c.deaths - lag(c.deaths,14) over(partition by c.fips order by c.date) as two_weekly_deaths,
           --using slq window function to sum two-weekly new deaths on rolling bases
      ruc.population_2010,
      round((c.cases - lag(c.cases,14) over (partition by c.fips order by c.date))/ruc.population_2010 * 100000,4)
            as two_weekly_cases_per_100k_people,
      round((c.deaths - lag(c.deaths,14) over (partition by c.fips order by c.date))/ruc.population_2010 * 100000,4)
            as two_weekly_deaths_per_100k_people
    from covid19.us_counties  as c
    left join covid19.rural_urban_codes_2013 as ruc
    on c.fips = ruc.FIPS
    where c.state = "Washington"
    order by c.county, c.date;

    """
    client = bigquery.Client(project='paul-henry-tremblay')
    results = client.query(sql)
    print(results)
    dates = []
    counties = []
    two_weekly_cases_per_100k_people = []
    #all_data = {}

    for i in results:
        date = i.get('date')
        dates.append(date)
        county = i.get('county')
        counties.append(county)
        two_weekly_case_per_100k_people = i.get(
            'two_weekly_cases_per_100k_people')

        two_weekly_cases_per_100k_people.append(
            two_weekly_case_per_100k_people)

    thresholds = [10 for x in range(0, len(dates))]
    print(thresholds)
    return (dates, counties, two_weekly_cases_per_100k_people, thresholds)


# Making a graph for two_weekly_case per 100k people for all counties in state of Washington
def two_weekly_case_per_100k_people_graph_bokeh(
    date, county, two_weekly_case_per_100k_people):

    #Specify the selection tools to be made available
    #select_tools = ['box_select', 'lasso_select', 'poly_select', 'tap', 'reset']

    # Format the tooltip
    tooltips = [('thresholds', '@thresholds'), ('date', '@date'),
                ('New confirmed cases per 100k people',
                 '@two_weekly_case_per_100k_people')]
    #Specify the file name to be saved in the same directory of this python code
    output_file("Counties_reopen_WA.html")

    #have to convert date to datetime. rather inconvenient but necessary
    date = [datetime.datetime(x.year, x.month, x.day) for x in date]
    p = figure(
        plot_height=600,
        plot_width=800,
        x_axis_type='datetime',
        title='@county',
        y_axis_label='New Confirmed cased/100k people',
        toolbar_location="below",
    )
    p.line(x=date,
           y=two_weekly_case_per_100k_people,
           line_width=2,
           color='red',
           legend_label='urban')
    p.add_tools(HoverTool(tooltips=tooltips))

    show(p)


dates, county, two_weekly_case_per_100k_people, threholds = get_data()
two_weekly_case_per_100k_people_graph_bokeh(dates, county == "King",
                                            two_weekly_case_per_100k_people)
"""
def get_data_h():
    all_data, thresholds  = get_data()

def main()
    get_data_h()
    # do something with the data

if __name__ == '__main__':
    main()

"""
