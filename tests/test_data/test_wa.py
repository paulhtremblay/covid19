 """
 Google Bigquery SQL query test and matplot test
 The data is hosted in Google Cloud Bigg query,project ='paul-henry-tremblay'.
 The below function is for testing if can get data from the above project via SQL query.
 Also, based on the data, if can make a graph via matplotlib.
 """

import datetime
from google.cloud import bigquery
from matplotlib.pyplot import plot_date, axis, show, gcf


def get_state_data():
    sql = """select date, cases from `paul-henry-tremblay.covid19.us_states`
        where state = 'Washington'
	order by date;
	"""
    client = bigquery.Client(project='paul-henry-tremblay')
    result = client.query(sql)
    final = []

    for i in result:
        date = i.get('date')
        cases = i.get('cases')
        final.append([date, cases])
    return final


def cases_by_date_graph(final):
    dates = [i[0] for i in final]
    cases = [i[1] for i in final]
    plot_date(dates, cases, "-o", color="blue", markeredgecolor="black")
    gcf().autofmt_xdate()
    show()


sd = get_state_data()
cases_by_date_graph(sd)
