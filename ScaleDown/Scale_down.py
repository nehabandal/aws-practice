import sys
import requests
import boto3
import json
from requests_aws4auth import AWS4Auth


class ScaleOps:
    '''
    Generate sts token to access API
    '''

    def get_temp_credential(self, role_name, REGION, ACCESS, SECRET):
        client = boto3.client('sts',
                              region_name=REGION,
                              aws_access_key_id=ACCESS,
                              aws_secret_access_key=SECRET,
                              )
        response = client.assume_role(
            RoleArn=role_name,
            RoleSessionName='api-access-example'
        )
        access_key = response['Credentials']['AccessKeyId']
        secret_key = response['Credentials']['SecretAccessKey']
        token = response['Credentials']['SessionToken']
        return (access_key, secret_key, token)

    '''
    Send POST request to execute API
    '''

    def apigw_client(self, request_url, data, service_method):
        aws_auth = {
            "AccessKeyId": access_key,
            "SecretKey": secret_key,
            "SessionToken": token
        }
        headers = {
            'Content-Type': 'application/json'
        }
        if token is not None:
            auth = AWS4Auth(aws_auth["AccessKeyId"], aws_auth["SecretKey"], region, service,
                            session_token=aws_auth["SessionToken"])
        else:
            auth = AWS4Auth(aws_auth["AccessKeyId"], aws_auth["SecretKey"], region, service)
        response = requests.request(service_method, request_url, data=data, auth=auth, headers=headers)
        return response.text

    def check_execution_status(self, executionArn):
        endpoint = 'https://api.troposphere.tcie.pro/status/prod/describe'

        payload = {
            "executionArn": "%s" % executionArn
        }
        payload_str = json.dumps(payload)
        return self.apigw_client(endpoint, payload_str, 'POST')


if __name__ == "__main__":

    region = 'us-west-2'
    service = 'execute-api'
    scale_ops = ScaleOps()
    region_name = sys.argv[1]
    tenant_name = sys.argv[2]
    ACCESS = sys.argv[3]
    SECRET = sys.argv[4]
    role_name_API_access = 'arn:aws:iam::664529841144:role/CrossAccountAPIGatewayProdStageAccess'
    (access_key, secret_key, token) = scale_ops.get_temp_credential(role_name_API_access, region_name, ACCESS, SECRET)
    # print(access_key)
    # print(secret_key)
    # print(token)

    endpoint = 'https://api.troposphere.tcie.pro/scale/prod/execute'

    region_tenant_name = {'region': region_name, 'tenant': tenant_name}

    '''
    API call for Scale down
    '''
    with open('payload_scale_down.json') as f:
        payload = json.load(f)

    payload.update(region_tenant_name)

    payload_str = json.dumps(payload)
    response_down = scale_ops.apigw_client(endpoint, payload_str, 'POST')

    result = json.loads(response_down)
    print(result)

    try:
        '''
        Saving execution ARN for ASG
        '''
        if 'executionArn' in result:
            print(json.loads(scale_ops.check_execution_status(result['executionArn'])))

            while json.loads(scale_ops.check_execution_status(result['executionArn']))['status'] == "RUNNING":
                scale_ops.check_execution_status(result['executionArn'])
            print(scale_ops.check_execution_status(result['executionArn']))

    except Exception as e:
        print("Exception occured while running Scale down API")
