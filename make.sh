set -e
rm html_temp/* 2> /dev/null || echo 
rm html_temp/states/* 2> /dev/null || echo
python us_states_rt.py  
python us_states_rates.py
python make_html_index.py
python incidents_over_time.py
python make_wa_html.py
python make_territories.py
#gsutil web set -m index.html -e 404.html gs://www.paulhtremblay.com
python  upload_html_to_bucket.py


