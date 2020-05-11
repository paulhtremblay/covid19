import boto3
import os
import glob


def upload_to_storage(local_path, bucket_name, object_name):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. 
    """
    return
    with open(local_path, 'rb') as read_obj:
        b = b''.join(read_obj.readlines())
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.put_object(Key = object_name,
        Body = b, 
        ContentType='text/html',
        CacheControl='max-age=60, public',
        ) 

def upload_html(bucket_name = 'seattle-data.com'):
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

if __name__ == '__main__':
    upload_html()

"""
if __name__ == '__main__':
    file_name = '/home/henry/Downloads/test_upload.html'
    bucket = 'seattle-data.com'
    upload_file(file_name, bucket, object_name='test_upload3.html')
"""
