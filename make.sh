set -e
rm html_temp/* 2> /dev/null || echo 
rm html_temp/states/* 2> /dev/null || echo
python us_states_rt.py  
python us_states_rates.py
python washington_state.py
python make_territories.py
python make_index_404.py
#gsutil web set -m index.html -e 404.html gs://www.paulhtremblay.com
#python  upload_html_to_bucket.py


