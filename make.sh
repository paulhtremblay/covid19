set -e
rm html_temp/*
python us_states_rt.py  
python us_states_rates.py
python make_html_rt.py 
python make_html.py 
#gsutil web set -m index.html -e 404.html gs://www.henry-data.com
python  upload_html_to_bucket.py


