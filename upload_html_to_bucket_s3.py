import boto3
import os
import glob
import argparse

def _get_args():
    parser = argparse.ArgumentParser(description='upload')
    parser.add_argument('--verbose', '-verbose', action='store_true', help='Oracle base table name')
    parser.add_argument('--branch', '-b', choices = ['dev', 'prod'], required = True,
            help='branch of git')
    return parser.parse_args()



def upload_to_storage(local_path, bucket_name, object_name):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. 
    """
    with open(local_path, 'rb') as read_obj:
        b = b''.join(read_obj.readlines())
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.put_object(Key = object_name,
        Body = b, 
        ContentType='text/html',
        CacheControl='max-age=60, public',
        ) 

def upload_html(bucket_name ):
    files = glob.glob('html_temp/*.html')
    for i in files:
        head, tail = os.path.split(i)
        upload_to_storage(local_path = i, bucket_name = bucket_name,
                object_name = tail)
    files2 = glob.glob('html_temp/states/*.html')
    for i in files2:
        head, tail = os.path.split(i)
        upload_to_storage(local_path = i, bucket_name = bucket_name,
                object_name = 'states/{name}'.format(name = tail))

def get_bucket_name(branch):
    if branch == 'dev':
        return 'seattle-data-dev'
    elif branch == 'prod':
        raise NotImplementedError()
    else:
        raise ValueError('no if')

if __name__ == '__main__':
    args = _get_args()
    upload_html(get_bucket_name(args.branch))

