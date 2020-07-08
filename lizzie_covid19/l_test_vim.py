import l_common as c
import itertools as it
import operator
import datetime

sql_str = """
    select date, state, county,
    cases-lag(cases, 1) over(partition by county order by date) as daily_cases,
    deaths-lag(deaths,1) over(partition by county order by date) as daily_deaths
    from covid19.us_counties
    where state in ('Washington', 'Alabama')
    and date > date_sub(current_date(), interval 1 MONTH)
    and lower(substr(county,1,1)) in ('a','k')
    order by state, county, date"""

col_names = ['date', 'state', 'county', 'daily_cases', 'daily_deaths']

df = c.dataframe_from_sql(col_names, sql_str)
# source = ColumnDataSource(df)

# c.all_counties_graph('Washington', df)
# c.all_counties_graph('Alabama', df)
c.list_of_state_graph(["Alabama", "Washington"], df)
