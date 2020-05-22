from time import time
import sys
import boto3

client = boto3.client('cloudfront')
# Uncomment this to pass a URL to the script
#def get_id(url):
#    print("get_id args: {0}".format(url))
#    # url: asdf.cloudfront.net
#    # return: E2134123ASDF
#    # where E2134123ASDF is the id of asdf.cloudfront.net
#    paginator = client.get_paginator('list_distributions')
#    response_iterator = paginator.paginate()
#    for i in response_iterator:
#        for j in i['DistributionList']['Items']:
#            if j['Aliases']['Items'][0] == url:
#                return j['Id']

paths = ['index.html']
i =  ['/{}'.format(f) for f in paths]
print(i)
response = client.create_invalidation(
    #DistributionId=get_id(sys.argv[1]),
    DistributionId='E1GMJOB0CSGHTR',
    InvalidationBatch={
        'Paths': {
            'Quantity': len(paths),
            'Items': ['/{}'.format(f) for f in paths],
            },
        'CallerReference': str(time()).replace(".", "")
        }
    )
print(response)
