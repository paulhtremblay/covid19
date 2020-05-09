set -e
rm html_temp/* || echo 
rm html_temp/states/* || echo
python us_states_rt.py  
python us_states_rates.py
python make_html_rt.py 
python make_html_index.py
python incidents_over_time.py
python make_wa_html.py
python make_territories.py
#gsutil web set -m index.html -e 404.html gs://www.paulhtremblay.com
python  upload_html_to_bucket.py


