# sql pivot
# sql_str is to run some simple sql query to get a table
# the vals(value) are for the field


from google.cloud import bigquery



def sql_pivot(sql_str, pivot_field, order_by_fields, vals, sum_over_field):
    str = ''
    str = str + f"select \n\t{comma_seperated_lst(order_by_fields)}"
    for item in vals: 
        sum_str = f"\t,coalesce(sum(case when {pivot_field} = '{item.replace(' ', '_')}' then {sum_over_field} end),0) as {item.replace(' ', '_')}"
        str = str + '\n' + sum_str 

    str = str + f"\n\t,sum({sum_over_field }) as total" + '\nfrom (' + sql_str + ') as sql_str_table'
    str = str + f"\ngroup by {comma_seperated_lst(order_by_fields)}\norder by {comma_seperated_lst(order_by_fields)}"
    return str

def comma_seperated_lst(lst):
    return ', '.join(f"{i}" for i in lst)

# This is for get result from sql
def get_sql(sql):
    client = bigquery.Client(project='paul-henry-tremblay')
    results = client.query(sql)

sql = '''
     select
            date,
            state,
            cases-lag(cases,1,0) over(partition by state order by date) as daily_cases
      from  covid19.us_states
      '''
pivot_field = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'District of Columbia', 'Florida', 'Georgia', 'Guam', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Northern Mariana Islands', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Puerto Rico', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virgin Islands', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
print(sql_pivot(sql, 'state', ['date'], pivot_field, 'daily_cases'))

# to get a list of pivot_field from bigquery
'''select "['" string_agg(distinct state, "', '" order by state
) from covid19.us_states'''
