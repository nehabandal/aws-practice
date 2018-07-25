from __future__ import print_function
import boto3
import json

import os
import sys
import uuid
from PIL import Image
import PIL.Image

iam = boto3.client('iam')

my_managed_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "RESOURCE_ARN"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:DeleteItem",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Scan",
                "dynamodb:UpdateItem"
            ],
            "Resource": "RESOURCE_ARN"
        }
    ]
}

response = iam.create_policy(
  PolicyName='AWSLambdaExecute',
  PolicyDocument=json.dumps(my_managed_policy)
)

