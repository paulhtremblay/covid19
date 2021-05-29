import csv
import os
from google.cloud import bigquery
import datetime

def us_cum_sql():
    return """
    with hosp as
(
SELECT date, coalesce(sum( currently_hospitalized ),0) as hos,
coalesce(sum(new_hospitalized),0) as new_hos
FROM `paul-henry-tremblay.covid19.hospitalized_by_day`
group by date
),
cases_t as
(SELECT date, coalesce(sum( new_cases ),0) as cases,
coalesce(sum( new_deaths ),0) as deaths
FROM `paul-henry-tremblay.covid19.us_states_day_diff`
group by date
)
select h.date, cases, deaths, hos, new_hos
from hosp h
inner join
cases_t c
on c.date = h.date
    """

def get_data_mask_usa():
    return """
    with masked_dates as
(
SELECT c.date, c.state, c.new_deaths, c.new_cases, m.date as mask_date
FROM `paul-henry-tremblay.covid19.us_states_day_diff` c
left join covid19.masks_states m
on m.state = c.state
where c.state != 'Kansas'
),
masked_dates_kansas as
(SELECT c.date, c.county, c.state, c.new_deaths, c.new_cases, m.date as mask_date
FROM `paul-henry-tremblay.covid19.us_counties_diff` c
left join covid19.masks_kansas m
on m.county = c.county
where c.state = 'Kansas'
),
pop as
(select state, population_2019 as population
from covid19.population_2019_est
where state = county
),
pop_kansas as
(select county, fips, population_2019 as population
from covid19.population_2019_est
where state != county
and state = 'Kansas'
),
true_infected_ as
(select i.date, s.state_long as state, i.new_infected_mean as infected
from covid19.infection_estimates i
inner join covid19.state_conversion s
on s.state_code = i.state
),
true_infected_kansas_ as
(select i.date, s.state_long as state, county, fips, i.new_infected_mean as infected
from covid19.infection_estimates_counties i
inner join covid19.state_conversion s
on s.state_code = i.state
where s.state_long = 'Kansas'
),
true_infected as
(select t.*, new_deaths, new_cases, mask_date
from true_infected_ t
inner join masked_dates m
on m.date = t.date
and m.state = t.state
),
true_infected_kansas as
(select t.*, new_deaths, new_cases, mask_date
from true_infected_kansas_ t
inner join masked_dates_kansas m
on m.date = t.date
and m.state = t.state
and m.county = t.county
),

with_pop as
(select m.*, p.population
from true_infected m
inner join pop p
on p.state = m.state
),
with_pop_kansas as
(select m.*, p.population
from true_infected_kansas m
inner join pop_kansas p
on p.fips = m.fips
),

mask_no_mask as
(select p.date, p.state,
case
  when mask_date is null or date < DATE_ADD(mask_date, INTERVAL 5 DAY) then new_deaths else 0
end as no_mask_deaths,
case
  when date >= DATE_ADD(mask_date, INTERVAL 5 DAY) then new_deaths else 0
end as mask_deaths,
case
  when mask_date is null or date < DATE_ADD(mask_date, INTERVAL 5 DAY) then new_cases else 0
end as no_mask_cases,
case
  when date >= DATE_ADD(mask_date, INTERVAL 5 DAY) then new_cases else 0
end as mask_cases,
case
  when mask_date is null or date < DATE_ADD(mask_date, INTERVAL 5 DAY) then infected else 0
end as no_mask_infections,
case
  when date >= DATE_ADD(mask_date, INTERVAL 5 DAY) then infected else 0
end as mask_infections,
case
  when mask_date is null or date < DATE_ADD(mask_date, INTERVAL 5 DAY) then population else 0
end as no_mask_population,
case
  when date >= DATE_ADD(mask_date, INTERVAL 5 DAY) then population else 0
end as mask_population
from with_pop p
),
mask_no_mask_kansas as
(select p.date, 'Kansas' as state,
case
  when mask_date is null or date < DATE_ADD(mask_date, INTERVAL 5 DAY) then new_deaths else 0
end as no_mask_deaths,
case
  when date >= DATE_ADD(mask_date, INTERVAL 5 DAY) then new_deaths else 0
end as mask_deaths,
case
  when mask_date is null or date < DATE_ADD(mask_date, INTERVAL 5 DAY) then new_cases else 0
end as no_mask_cases,
case
  when date >= DATE_ADD(mask_date, INTERVAL 5 DAY) then new_cases else 0
end as mask_cases,
case
  when mask_date is null or date < DATE_ADD(mask_date, INTERVAL 5 DAY) then infected else 0
end as no_mask_infections,
case
  when date >= DATE_ADD(mask_date, INTERVAL 5 DAY) then infected else 0
end as mask_infections,
case
  when mask_date is null or date < DATE_ADD(mask_date, INTERVAL 5 DAY) then population else 0
end as no_mask_population,
case
  when date >= DATE_ADD(mask_date, INTERVAL 5 DAY) then population else 0
end as mask_population
from with_pop_kansas p
),
mask_no_mask_kansas2 as
(
select date, max(state) as state, sum(no_mask_deaths) as no_mask_deaths,
sum(mask_deaths) as mask_deaths,
sum(no_mask_cases) as no_mask_cases,
sum(mask_cases) as mask_cases,
sum(no_mask_infections) as no_mask_infections,
sum(mask_infections) as mask_infections,
sum(no_mask_population) as no_mask_population,
sum(mask_population) as mask_population
from mask_no_mask_kansas
group by date
),
both as
(select * from mask_no_mask_kansas2
union all
select * from mask_no_mask
),
usa as
(select date,
sum(no_mask_deaths) as no_mask_deaths,
sum(mask_deaths) as mask_deaths,
sum(no_mask_cases) as no_mask_cases,
sum(mask_cases) as mask_cases,
sum(no_mask_infections) as no_mask_infections,
sum(mask_infections) as mask_infections,
sum(mask_population) as mask_population,
sum(no_mask_population) as no_mask_population
from both
group by date
)

select *
from  usa

    """

def get_party_state_cases_sql():
    return """
    select distinct s.state, s.cases, s.deaths, p.population_2019 as population,
e.result as party
from `paul-henry-tremblay.covid19.us_states` s
inner join `paul-henry-tremblay.covid19.population_2019_est` p
on p.state = s.state
inner join `paul-henry-tremblay.covid19.election_2020` e
on e.state = p.state
where s.date = (select max(date) from  `paul-henry-tremblay.covid19.us_states`)
and p.county = p.state
    """


def get_state_masks():
    return """
    SELECT *
    FROM `paul-henry-tremblay.covid19.masks_states` t
    order by state
    """

def get_hospitals_sql():
    return """
    SELECT date, state, currently_hospitalized as hospitalized_currently, new_hospitalized
FROM `paul-henry-tremblay.covid19.hospitalized_by_day`
order by date
    """

def get_hospitals_sql_old():
    return """
    select date, state_name as state, 
    current_hospitalizations as hospitalized_currently
    FROM `paul-henry-tremblay.covid19.hospitals` 

    """
    #date,state,hospitalized_currently,death_increase,positive_increase

def get_sql_masks_kansas_sql():
    return """
    with t1 as
(
select c.date, c.county, c.new_cases
from covid19.us_counties_diff c
where state = 'Kansas'
),
pop as
(select replace(county, ' County', '') as county, population_2019
from covid19.population_2019_est
where state = 'Kansas'
),
t2 as
(select county, date_add(date, interval 5 day) as date
from covid19.masks_kansas
),
t3 as
(select t1.date, t1.county, t1.new_cases,
t2.date as mask_start,
case when t2.date is null then false
when t1.date >= t2.date then true
when t1.date < t2.date then false
else null
end as mask
from t1
left join t2
on t1.county = t2.county
),
with_pop as
(select t3.*, new_cases/population_2019 * 10000 as per_pop
from t3
inner join pop p
on p.county = t3.county
),
t4 as
(select date,
sum (case when mask then new_cases else 0 end) as masked,
sum (case when not  mask then new_cases else 0 end) as non_masked,
sum (case when not  mask then per_pop else 0 end) as non_masked_pop,
sum (case when   mask then per_pop else 0 end) as masked_pop,
from with_pop
group by date
)
select * from t4
order by date
    """

def get_sates_tracker_sql():
    return """
    with t1 as
(
SELECT date, state_long as state, total_test_results, positive_cases_viral, positive, negative,
total_test_results_increase, positive_increase, death_increase
FROM `paul-henry-tremblay.covid19.covid19_track_states` c
inner join covid19.state_conversion sc
on sc.state_code = c.state
--where state = 'WA'
), t2 as
(select *
from `paul-henry-tremblay.covid19.us_states_day_diff`
--where state = 'Washington'
)
select t1.*, new_cases, new_deaths
from t1
inner join t2
on t1.date = t2.date
and t1.state = t2.state
order by t1.date
    """

def get_non_king_slq():
    return """
    SELECT date,  sum(new_cases) as cases,
sum(new_deaths) as deaths
FROM `paul-henry-tremblay.covid19.us_counties_diff`
where state = 'Washington'
and county != 'King'
--and date > '2020-06-01'
group by date
order by date
    """

def get_state_totals_sql():
    return """
    SELECT state, cases, deaths
FROM `paul-henry-tremblay.covid19.us_states`
where date = (select max(date) from `paul-henry-tremblay.covid19.us_states`)
    """

def get_7_day_state():
    return """
    SELECT u.state, date, new_deaths, new_cases,
AVG(new_deaths) OVER (ORDER BY date ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS seven_rolling_deaths,
AVG(new_cases) OVER (ORDER BY date ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS seven_rolling_cases,
population_2019 as population
FROM `paul-henry-tremblay.covid19.us_states_day_diff` u
inner join covid19.population_2019_est p
on p.state = u.state
where p.state = p.county
    """

def get_7_day_county():
    return """
     with ny_pop as
 (select sum(population_2019) as population
 from covid19.population_2019_est
 where state = 'New York'
 and  county in ('Kings County', 'Queens County', 'Bronx County', 'New York County')
 )
 SELECT u.state, u.county, date, new_deaths, new_cases,
 case when u.county = 'New York City' then (select population from ny_pop) else
population_2019 end as population,
rucc_2013
FROM `paul-henry-tremblay.covid19.us_counties_diff` u
inner join covid19.population_2019_est p
on p.fips = u.fips
inner join covid19.rural_urban_codes_2013 r
on r.fips = u.fips
    """

def get_pop_state():
    return """
    SELECT state, population_2019
FROM `paul-henry-tremblay.covid19.population_2019_est`
where state = county
    """

def get_state_sql_day_cum():
    return """
    SELECT date, state, cases, deaths
FROM `paul-henry-tremblay.covid19.us_states`
order by date
    """

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

def get_sql_world_day_old():
    return  """
    /* WORLD BY DAY */
  SELECT  date, country, cases, deaths
FROM `paul-henry-tremblay.covid19.world`
order by date
  """

def get_sql_world_day():
    return  """
    /* WORLD BY DAY */
  SELECT  date, country, new_cases as cases, new_deaths as deaths,
  population
FROM `paul-henry-tremblay.covid19.world2`
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
sum(new_cases) as cases,
sum(new_deaths) as deaths
from covid19.world2
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
case when the_rank <= 4 then c.county else 'other' end as county,
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


def get_timestamp():
    return  """
    /* LAST UPDATED */
  SELECT  TIMESTAMP_MILLIS(last_modified_time) as last_updated
FROM `covid19.__TABLES__` where table_id = 'us_states'
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
    gen_writer(client = client, sql = us_cum_sql(),
            path = 'us_cum.csv')
    gen_writer(client = client, sql = get_data_mask_usa(),
            path = 'masks_us.csv')
    gen_writer(client = client, sql = get_state_masks(),
            path = 'masks_states.csv')
    gen_writer(client = client, sql = get_party_state_cases_sql(),
            path = 'party_cases_deaths_pop.csv')
    gen_writer(client = client, sql = get_state_totals_sql(),
            path = 'states_totals.csv')
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
    gen_writer(client = client, sql =get_state_sql_day_cum(), 
            path = 'states_cum.csv')
    gen_writer(client = client, sql =get_pop_state(), 
            path = 'states_population.csv')
    gen_writer(client = client, sql =get_7_day_state(), 
            path = 'seven_day_state.csv')
    gen_writer(client = client, sql =get_non_king_slq(), 
            path = 'non_king.csv')
    gen_writer(client = client, sql =get_7_day_county(), 
            path = 'seven_day_county.csv')
    gen_writer(client = client, sql = get_timestamp(),
            path = 'site_last_updated.csv')
    gen_writer(client = client, sql =get_sates_tracker_sql(), 
            path = 'covid_tracker_states.csv')
    gen_writer(client = client, sql =get_sql_masks_kansas_sql(), 
            path = 'kansas_masks.csv')
    gen_writer(client = client, sql =get_hospitals_sql(), 
            path = 'hospital.csv')

if __name__ == '__main__':
    get_all_data()
