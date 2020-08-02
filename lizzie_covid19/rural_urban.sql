select 
	t3.date
	t3.state,
	t3.ru_code
	t3.daily_cases,
	t3.daily_deaths,
	round(t3.daily_cases/t3.population *100000,2),
	round(t3.daily_deaths/t3.population *100000,2)

from(
     select 
         t1.date,
         t1.state,
         t1.ru_code, 
         t1.cases, 
         t1.cases - lag(t1.cases) over(partition by t1.state, t1.ru_code order by t1.date) as  daily_cases,
         t1.deaths,t1.deaths - lag(t1.deaths) over(partition by t1.state, t1.ru_code order by t1.date) as daily_deaths, 
         t2.population
      
     from(
          select 
               c.date, 
               c.state, 
               case when ruc.rucc_2013 <= 3 then 'U' else 'R' end as ru_code, 
               sum(c.cases) as cases, sum(c.deaths) as deaths
          from covid19.us_counties as c
          join covid19.rural_urban_codes_2013 ruc
          on ruc.FIPS = c.fips
          group by c.date, c.state, ru_code
          order by c.state, ru_code, c.date
        
         ) as t1
   
    join covid19.state_conversion as sc
    on sc.state_long = t1.state
    join(
         select 
              state,
              case when ruc.rucc_2013 <= 3 then 'U' else 'R' end as ru_code,
              sum(population_2010) as population
         from covid19.rural_urban_codes_2013 as ruc
         group by state, ru_code
         ) as t2

   on t2.state = sc.state_code
   where t1.ru_code = t2.ru_code
   and t1.state = 'Washington'
   order by state, ru_code, date
   
   ) as t3

order by state, ru_code, date


