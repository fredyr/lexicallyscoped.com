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

"""
Uploading file _site/404.html
Uploading file _site/atom.xml
Uploading file _site/cv.html
Uploading file _site/dummy.txt
Uploading file _site/index.html
Uploading file _site/README.md
Uploading file _site/TODO.txt
Uploading file _site/2012/11/09/lexically-scoped-up.html
Uploading file _site/2012/11/25/groovy-introduction.html
Uploading file _site/2012/12/31/systems-design.html
Uploading file _site/2013/01/02/functional-programming.html
Uploading file _site/2013/03/17/ansible.html
Uploading file _site/css/styles.css
Uploading file _site/css/syntax.css
Uploading file _site/img/me_round.png
"""

# TODO Invalidate the cloudfront with a list of the uploaded files!
#cf = boto.connect_cloudfront()
#cf.create_invalidation_request("distribution_id", ["/path1", "/path2"])
