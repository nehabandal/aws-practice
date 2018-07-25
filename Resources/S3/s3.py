
import json

import boto3
import os
import sys
import uuid
from PIL import Image
import PIL.Image
# from voter_lists_online_service_NB import VoterListsOnlineService
import datetime


class S3Class:
    def create_Bucket(self, s3):
        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        print("Bucket List: %s" % buckets)

        s3.create_bucket(Bucket='neha-srcbucket', CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})
        s3.create_bucket(Bucket='neha-srcbucket-resized', CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})

    def upload_file_bucket(self,s3):
        filename = 'Grad.jpg'
        bucket_name = 'neha-srcbucket'
        s3.upload_file(filename, bucket_name, filename)

    # def resize_image(image_path, resized_path):
    #     with Image.open(image_path) as image:
    #         image.thumbnail(tuple(x / 2 for x in image.size))
    #         image.save(resized_path)
    #
    # def handler(event, self, s3):
    #     for record in event['Records']:
    #         bucket = record['s3']['bucket']['name']
    #         key = record['s3']['object']['key']
    #         download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
    #         upload_path = '/tmp/resized-{}'.format(key)
    #
    #         s3.download_file(bucket, key, download_path)
    #         self.resize_image(download_path, upload_path)
    #         s3.upload_file(upload_path, '{}resized'.format(bucket), key)
'''
S3 operations start here
'''

if __name__ == '__main__':

    s3 = boto3.client('s3')

    s3_obj = S3Class()

    print('Perform different s3 bucket operations')

    # print data
    # s3_obj.create_Bucket(s3)
    s3_obj.upload_file_bucket(s3)
