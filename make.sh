set -e
BRANCH=`git rev-parse --abbrev-ref HEAD`
cp -R templates/styles html_temp/styles
rm html_temp/* 2> /dev/null || echo 
rm html_temp/states/* 2> /dev/null || echo
python us_states_rt.py  
python us_states_rates.py
python washington_state.py
python make_territories.py
python make_index_404.py
if [ $BRANCH == 'development' ]; then
	python upload_html_to_bucket_s3.py --branch dev

elif [ $BRANCH == 'development' ]; then
	python upload_html_to_bucket_s3.py --branch prod
else
	echo Not uploading because not dev or prod
fi
# copy styles


