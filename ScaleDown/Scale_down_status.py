import sys
import requests
import boto3
import logging
import datetime
import json
from requests_aws4auth import AWS4Auth
from prettytable import PrettyTable


def get_temp_credential(role_name, REGION, ACCESS, SECRET):
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


class ScaleOps:

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


class ScaleCheck:

    def conn_test(self, client, asg_name):
        response = client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[
                asg_name,
            ],

        )
        return response

    def find_capacity(self, response):
        # print(response['AutoScalingGroups'][0]['AutoScalingGroupName'])
        for asg in response['AutoScalingGroups']:
            min_capacity = (asg['MinSize'])
            max_capacity = (asg['MaxSize'])
            desired_capacity = (asg['DesiredCapacity'])
            return min_capacity, max_capacity, desired_capacity

    def check_scale_down(self, asg_name, min_capacity, max_capacity, desired_capacity):
        try:
            assert min_capacity == 0 and max_capacity == 0 and desired_capacity == 0
            flag = True
            logging.info("Scaled down: %s" % asg_name)

        except AssertionError as e:
            flag = False
            logging.error("Failed to Scale down: %s" % asg_name)

        if flag:
            return "Success", asg_name
        else:
            return "Failed", asg_name


if __name__ == "__main__":

    region = 'us-west-2'
    service = 'execute-api'
    scale_ops = ScaleOps()
    region_name = sys.argv[1]
    tenant_name = sys.argv[2]
    ACCESS = sys.argv[3]
    SECRET = sys.argv[4]

    role_name_API_access = 'arn:aws:iam::664529841144:role/CrossAccountAPIGatewayProdStageAccess'
    (access_key, secret_key, token) = get_temp_credential(role_name_API_access, region_name, ACCESS, SECRET)
    # print(access_key)
    # print(secret_key)
    # print(token)

    endpoint = 'https://api.troposphere.tcie.pro/scale/prod/execute'

    region_tenant_name = {'region': region_name, 'tenant': tenant_name}

    '''
    API call for Scale status
    '''
    with open('payload_scale_down_status.json') as f:
        payload = json.load(f)

    payload.update(region_tenant_name)

    payload_str = json.dumps(payload)
    print(payload_str)
    response = scale_ops.apigw_client(endpoint, payload_str, 'POST')

    result = json.loads(response)
    print(result)

    '''
    Saving execution ARN for ASG
    '''
    out_res = {}
    if 'executionArn' in result:
        print(json.loads(scale_ops.check_execution_status(result['executionArn'])))

        while json.loads(scale_ops.check_execution_status(result['executionArn']))['status'] == "RUNNING":
            scale_ops.check_execution_status(result['executionArn'])
        print(scale_ops.check_execution_status(result['executionArn']))
        out_res = scale_ops.check_execution_status(result['executionArn'])
        print(out_res)

    '''
    Creating list of ASG names to check scale down status
    '''
    try:
        data = json.loads(out_res)
        print(data)
        asg_output = data["output"]

        asg_output = json.loads(asg_output)
        asg_details = asg_output["asg"]

        list_asg = list(asg_details.keys())
        assert len(list_asg) > 2  # 2 because 1 is for 'tenant' and second is for 'scaleOps'

        ''''
        Overriding region as default is set in configuration file and there are different
        regions of autoscaling groups, so set region to payload region
        for auto-scaling(shared credentials) not access key or token we got
        for api access
        '''
        scale_check = ScaleCheck()
        role_name_shared_account = 'arn:aws:iam::168895513848:role/TIBCO/Administrator'
        (access_key_scale_check, secret_key_scale_check, token_scale_check) = get_temp_credential(
            role_name_shared_account, region_name, ACCESS, SECRET)
        # print(access_key)
        # print(secret_key)
        # print(token)

        client = boto3.client('autoscaling',
                              region_name=region_name,
                              aws_access_key_id=access_key_scale_check,
                              aws_secret_access_key=secret_key_scale_check,
                              aws_session_token=token_scale_check,
                              )

        '''
        Finding and validating capacity of each autoscaling group after scale down
        '''
        x = PrettyTable(border=True, header=True, padding_width=3)
        x.field_names = ['Auto Scaling Group', 'Min capacity', 'Max capacity', 'Desired capacity', 'Status',
                         'Date Time']
        flag = False
        subj = {}
        for asg_name in list_asg:
            if asg_name != 'scaleOps' and asg_name != 'tenant':
                resp = scale_check.conn_test(client, asg_name)
                # print("Current Scaling capacity for ASG", asg_name)
                min_capacity, max_capacity, desired_capacity = scale_check.find_capacity(resp)
                # print(min_capacity, max_capacity, desired_capacity)
                status, asg_name = scale_check.check_scale_down(asg_name, min_capacity, max_capacity,
                                                                desired_capacity)
                subj[asg_name] = status
                x.add_row([asg_name, min_capacity, max_capacity, desired_capacity, status, datetime.datetime.now()])

        '''
           Creating html file to add status and validation results(including min,max and desired capacity) of Scaling group
        '''
        # print(subj)
        x.format = True
        x.border = True
        x.align["Auto Scaling Group"] = "l"
        if 'Failed' in subj.values():
            file_name = "scale_down_failed_%s_%s_%s.html" % (tenant_name, region_name, datetime.datetime.today().date())
        else:
            file_name = "scale_down_success_%s_%s_%s.html" % (
                tenant_name, region_name, datetime.datetime.today().date())

        fileout = open(file_name, 'w')
        sys.stdout = fileout
        print(x.get_html_string())
        fileout.close()

    except AssertionError as e:
        logging.error("No AutoScaling groups")
