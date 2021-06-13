set -e
rm -Rf main.py
rm -Rf  requirements.txt
cp upload_ny_times_github_to_storage.py main.py
cp requirements_storage.txt requirements.txt
zip us_states_nytgithub.zip main.py requirements.txt
python upload_to_lambda.py us_states_nytgithub.zip

rm -Rf main.py
rm -Rf  requirements.txt
cp upload_data_to_bq.py main.py
cp requirements_bq.txt requirements.txt
zip upload_to_bq.zip main.py requirements.txt
python upload_to_lambda.py upload_to_bq.zip


