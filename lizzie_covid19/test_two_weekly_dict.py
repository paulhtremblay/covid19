"""One of the criterias of reopening State Washington is new infections per
    100,000 people over a two-week period meeting some threshold, currently is
    6, it probably will be changed.
    The population in Washington by county, changed according to
     https://www.governor.wa.gov/sites/default/files/WACountiesCaseRate.pdf?utm_medium=email&utm_source=govdelivery
    apart no figures avaible in some counties like Astion etc.

"""

from google.cloud import bigquery
from bokeh.io import output_file, show
from bokeh.layouts import row
from bokeh.layouts import gridplot
from bokeh.plotting import figure


def get_data(key, values):
    sql = """

    --This query intends to get reuslts by county(fips code), if the cases are
    --not signed to a county,it will be shown as "unknown".


        select
            c.date,
            c.state,
            c.county,
            ruc.FIPS,
            c.cases as accum_cases,
            -- in table covid19.us_counties,the cases are accumulated to date
            c.deaths as accum_deaths,
            -- in table covid19.us_counties,the cases and deaths are accumulated to date
            c.cases - lag(c.cases,1) over (partition by c.fips order by c.date) as daily_cases,
            c.cases - lag(c.cases,14) over (partition by c.fips order by c.date) as two_weekly_cases,
            --using slq window function to sum two_weekly new cases on rolling bases
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
    """dict_c = {}
    for i in results:
        dict_c[key] = i.get('county')
        dict_c[values] = [
            i.get('date'),
            i.get('two_weekly_cases_per_100k_people')
        ]
        print(dict_c[key])
    return dict_c"""


    dates = []
    counties = []
    # two_weekly_cases = []
    two_weekly_cases_per_100k_people = []
    for i in results:
        date = i.get('date')
        county = i.get('county')
        # two_weekly_case = i.get('two_weekly_cases')
        two_weekly_case_per_100k_people = i.get(
            'two_weekly_cases_per_100k_people')
        dates.append(date)
        print(date)
        counties.append(county)
        print(county)
        # two_weekly_cases.append(two_weekly_case)
        two_weekly_cases_per_100k_people.append(
            two_weekly_case_per_100k_people)
        print(two_weekly_case_per_100k_people)
    thresholds = [6 for x in range(0, len(dates))]
    print(thresholds)
    dix ={'date':date,'county':county,'two_weekly_cases_per_100k_people':two_weekly_cases_per_100k_people} for date,county,two_weekly_cases_per_100k_people in zip(dates,counties,two_weekly_cases_per_100k_people)
    return (dates, two_weekly_cases_per_100k_people)


# Making graphs for two_weekly_case per 100k people for all counties in Washington State using Bokeh
def two_weekly_case_per_100k_people_graph(date,
                                          two_weekly_case_per_100k_people):
    plt.style.use('seaborn')
    plt.plot(dates, two_weekly_cases_per_100k_people, marker=".", linewidth=2)
    plt.plot(dates, thresholds, color='red', linewidth=3)
    plt.gcf().autofmt_xdate()
    # date_format = mpl_dates.DateFormatter('%b, %d')
    # plt.gca().xaxis.set_major_formatter(date_format)
    plt.tight_layout()
    #for county in counties:
    s1 = figure(background_fill_color="#fafafa")
    s1.circle(
        dates,
        two_weekly_cases_per_100k_people,
        #thresholds,
        size=12,
        alpha=0.8,
        color="#53777a")

    grid = gridplot([s1, None], ncols=2, plot_width=250, plot_height=250)
    show(grid)
    #savefig('bokeh_temp.png')


dates, two_weekly_cases_per_100k_people = get_data()
two_weekly_case_per_100k_people_graph(dates, two_weekly_cases_per_100k_people)"""
