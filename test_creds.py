from google.cloud import bigquery
#import os
from google.oauth2 import service_account

key_path = '/home/henry/Documents/biquery_key.json'

credentials = service_account.Credentials.from_service_account_file(
    key_path,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

client = bigquery.Client(
    credentials=credentials,
    project=credentials.project_id,
)
