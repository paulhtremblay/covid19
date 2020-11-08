set -e 
#bash -x make.sh 
echo "starting make at `date`"
VERBOSE=false
REFRESH_DATA=false
UPLOAD=false
source /home/henry/.bashrc
#P=$WORKON_HOME/covid19/bin/python
P=/home/henry/Envs2/covid19/bin/python
$P --version
 
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
	$P make_data.py
	$P make_poisson_data.py
fi


BRANCH=`git rev-parse --abbrev-ref HEAD`
rm -Rf html_temp
mkdir html_temp
rm -Rf includes
mkdir includes
cp -R templates/styles html_temp/styles
cp -R templates/javascript html_temp/javascript
$P make_nav.py
$P make_index_404.py
$P us_states_rates.py
$P make_territories.py
$P by_state.py
$P sweden.py
$P make_about.py
#python comparison_open.py
$P state_comparisons.py
$P data_table.py
$P by_counties.py
$P masks_states.py
$P state_comparisons.py
UPLOAD_TO=dev
if [ $BRANCH == 'master' ]; then
	UPLOAD_TO=prod
fi
if [ $UPLOAD == 'true' ] || [ $BRANCH == 'master' ]; then
	if [ $VERBOSE == 'true' ]; then
		echo uploading to ${UPLOAD_TO}
	fi
	$P upload_html_to_bucket_s3.py --branch ${UPLOAD_TO}
else
	echo Not uploading 
fi
# copy styles
echo "Successfully updated at `date`" 
