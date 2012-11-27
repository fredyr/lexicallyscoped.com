import boto
import os
from boto.s3.key import Key


def deploy_to_S3(bucket, directory):
    for path, d, files in os.walk(directory):
        for file in files:
            s3_filename = os.path.relpath(os.path.join(path, file), directory)
            local_path = os.path.join(path, file)
            k = Key(bucket)
            k.key = s3_filename
            print 'Uploading file %s' % local_path
            k.set_contents_from_filename(local_path)


conn = boto.connect_s3()
deploy_to_S3(conn.get_bucket('lexicallyscoped'), '_site')
