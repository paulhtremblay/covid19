set -e 
VERBOSE=false
REFRESH_DATA=false
UPLOAD=false

while getopts p:vru flag
do
    case "${flag}" in
		v) VERBOSE='true';;
		r) REFRESH_DATA='true';;
		u) UPLOAD='true';;
        p) username=${OPTARG};;
    esac
done
if [ $REFRESH_DATA == 'true' ]; then
	if [ $VERBOSE == 'true' ]; then 
		echo refreshing data
	fi
	python make_data.py
fi


BRANCH=`git rev-parse --abbrev-ref HEAD`
rm -Rf html_temp 
mkdir html_temp
cp -R templates/styles html_temp/styles
python us_states_rates.py
python make_territories.py
python by_state.py
python sweden.py
python make_index_404.py
python make_about.py
python data_table.py
UPLOAD_TO=dev
if [ $BRANCH == 'master' ]; then
	UPLOAD_TO=prod
fi
if [ $UPLOAD == 'true' ] || [ $BRANCH == 'master' ]; then
	if [ $VERBOSE == 'true' ]; then
		echo uploading to ${UPLOAD_TO}
	fi
	python upload_html_to_bucket_s3.py --branch ${UPLOAD_TO}
else
	echo Not uploading 
fi
# copy styles


