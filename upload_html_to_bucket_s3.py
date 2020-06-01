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



def upload_to_storage(local_path, bucket_name, object_name, 
        content_type= 'text/html; charset=utf-8'):
    """
    Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. 
    :param content_type: S3 http content mime-type (and encoding)
    """
    with open(local_path, 'rb') as read_obj:
        b = b''.join(read_obj.readlines())
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.put_object(Key = object_name,
        Body = b, 
        ContentType=content_type,
        CacheControl='max-age=60, public',
        ) 

def upload_html(bucket_name, verbose):
    files = glob.glob('html_temp/*')
    for i in files:
        head, tail = os.path.split(i)
        if os.path.isdir(i):
            continue
        upload_to_storage(local_path = i, bucket_name = bucket_name,
                object_name = tail)
    files2 = glob.glob('html_temp/states/*')
    for i in files2:
        head, tail = os.path.split(i)
        if verbose:
            print('uploading {t}'.format(t = tail))
        upload_to_storage(local_path = i, bucket_name = bucket_name,
                object_name = 'states/{name}'.format(name = tail))
    files3 = glob.glob('html_temp/countries/*')
    for i in files3:
        head, tail = os.path.split(i)
        if verbose:
            print('uploading {t}'.format(t = tail))
        upload_to_storage(local_path = i, bucket_name = bucket_name,
                object_name = 'countries/{name}'.format(name = tail))
    files4 = glob.glob('html_temp/counties/*')
    for i in files4:
        head, tail = os.path.split(i)
        if verbose:
            print('uploading {t}'.format(t = tail))
        upload_to_storage(local_path = i, bucket_name = bucket_name,
                object_name = 'counties/{name}'.format(name = tail))
    files5 = glob.glob('templates/styles/*')
    for i in files5:
        head, tail = os.path.split(i)
        if verbose:
            print('uploading {t}'.format(t = tail))
        upload_to_storage(local_path = i, bucket_name = bucket_name,
                object_name = 'styles/{name}'.format(name = tail),
                content_type = 'text/css'
                )

def get_bucket_name(branch):
    if branch == 'dev':
        return 'seattle-data-dev'
    elif branch == 'prod':
        return 'seattle-data.com'
    else:
        raise ValueError('no if')

if __name__ == '__main__':
    args = _get_args()
    upload_html(get_bucket_name(args.branch), verbose = args.verbose)

