import csv
import os
from google.cloud import bigquery

def get_sql_sweden():
    return """
    SELECT 'Seattle' as region, date,
sum (case when county = 'King' then new_cases else 0 end) as cases,
sum (case when county = 'King' then new_deaths else 0 end) as deaths
FROM `paul-henry-tremblay.covid19.us_counties_diff`
where state = 'Washington'
group by date
union all
SELECT 'New York City' as region, date,
sum (case when county = 'New York City' then new_cases else 0 end) as cases,
sum (case when county = 'New York City' then new_deaths else 0 end) as deaths
FROM `paul-henry-tremblay.covid19.us_counties_diff`
where state = 'New York'
group by date
union all
SELECT 'Washington' as region, date,
sum(new_cases) as cases,
sum(new_deaths) as deaths
FROM `paul-henry-tremblay.covid19.us_states_day_diff`
where state = 'Washington'
group by date
union all
SELECT 'New York' as region, date,
sum(new_cases) as cases,
sum(new_deaths) as deaths
FROM `paul-henry-tremblay.covid19.us_states_day_diff`
where state = 'New York'
group by date
union all
select 'Sweden',  date, cases, deaths from
covid19.world
where country = 'Sweden'
union all
select 'Belgium',  date, cases, deaths from
covid19.world
where country = 'Belgium'
union all
select 'Norway',  date, cases, deaths from
covid19.world
where country = 'Norway'
    """

def get_sql_world_day():
    return  """
    /* WORLD BY DAY */
  SELECT  date, country, cases, deaths
FROM `paul-henry-tremblay.covid19.world`
order by date
  """

def get_sql_world_week():
    return  """
    /* WORLD BY WEEK */
  select *
from
(
SELECT DATE_TRUNC(date, week) as date,
country,
sum(cases) as cases,
sum(deaths) as deaths
from covid19.world
group by date_trunc(date,week), country
) order by country, date
  """

def get_sql_us():
    return  """
    /* US */
    SELECT date, sum(cases) as cases, sum(deaths) as deaths 
    FROM `paul-henry-tremblay.covid19.us_states`
    group by date
    order by date
    """

def get_sql_cases_ranked():
    return  """
    /* STATE CASES */
    select * from 
    (
    select DATE_TRUNC(date, week) as date,
state,
county,
sum(cases) as cases, 
the_rank as `rank`
from
(
SELECT c.date,
c.state,
case when the_rank <= 3 then c.county else 'other' end as county,
c.new_cases as cases,
the_rank
FROM `paul-henry-tremblay.covid19.us_counties_diff` c
inner join covid19.cases_ranked_by_county r
on r.state = c.state
and r.county = c.county
)
group by date_trunc(date, week), county, state, the_rank
) order by date
    """


def get_state_sql_day():
    return  """
    /* STATE BY DAY */
  SELECT  date, state, new_cases as cases, new_deaths as deaths
FROM `paul-henry-tremblay.covid19.us_states_day_diff`
order by date
  """


def get_sql_deaths_ranked():
    return  """
    /* STATE DEATHS */
    select * from 
    (
    select DATE_TRUNC(date, week) as date,
state,
county,
sum(deaths) as deaths, 
the_rank as `rank`
from
(
SELECT c.date,
c.state,
case when the_rank <= 3 then c.county else 'other' end as county,
c.new_deaths as deaths,
the_rank
FROM `paul-henry-tremblay.covid19.us_counties_diff` c
inner join covid19.deaths_ranked_by_county r
on r.state = c.state
and r.county = c.county
)
group by date_trunc(date, week), county, state, the_rank
) order by date
    """

def gen_writer(client, sql, path):
    result = client.query(sql)
    with open(os.path.join('data', path), 'w') as write_obj:
        csv_writer = csv.writer(write_obj)
        counter = 0
        for i in result:
            counter += 1
            if counter == 1:
                csv_writer.writerow([x[0] for x in i.items()])
            csv_writer.writerow([x[1] for x in i.items()])

def get_all_data():
    client = bigquery.Client(project='paul-henry-tremblay')
    gen_writer(client = client, sql =get_sql_deaths_ranked(), 
            path = 'states_deaths_ranked.csv')
    gen_writer(client = client, sql =get_sql_cases_ranked(), 
            path = 'states_cases_ranked.csv')
    gen_writer(client = client, sql =get_state_sql_day(), 
            path = 'states.csv')
    gen_writer(client = client, sql =get_sql_us(), 
            path = 'us.csv')
    gen_writer(client = client, sql =get_sql_world_week(), 
            path = 'world_week.csv')
    gen_writer(client = client, sql =get_sql_world_day(), 
            path = 'world.csv')
    gen_writer(client = client, sql =get_sql_sweden(), 
            path = 'sweden_vs.csv')

    
if __name__ == '__main__':
    get_all_data()
