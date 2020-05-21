set -e 
VERBOSE=false
REFRESH_DATA=false

while getopts u:vr flag
do
    case "${flag}" in
		v) VERBOSE='true';;
		r) REFRESH_DATA='true';;
        u) username=${OPTARG};;
    esac
done
if [ $REFRESH_DATA == 'true' ]; then
	if [ $VERBOSE == 'true' ]; then 
		echo refreshing data
	fi
	python make_data.py
fi


BRANCH=`git rev-parse --abbrev-ref HEAD`
cp -R templates/styles html_temp/styles
rm html_temp/* 2> /dev/null || echo 
rm html_temp/states/* 2> /dev/null || echo
python us_states_rates.py
python make_territories.py
python by_state.py
python sweden.py
python make_index_404.py
UPLOAD_TO=dev
if [ $BRANCH == 'master' ]; then
	UPLOAD_TO=prod
fi
if [ $BRANCH == 'development' ] || [ $BRANCH == 'master' ]; then
	if [ $VERBOSE == 'true' ]; then
		echo uploading to ${UPLOAD_TO}
	fi
	python upload_html_to_bucket_s3.py --branch ${UPLOAD_TO}
else
	echo Not uploading because not dev or prod
fi
# copy styles


