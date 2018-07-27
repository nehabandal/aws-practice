import boto3
import json


class Ec2Class:
    def listInstance(selfself,ec2):
        instances = ec2.instances.filter( Filters = [{'Name':'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            print(instance.id, instance.instance_type)

    def createInstance(selfself,ec2):
        ec2.create_instances(ImageId='ami-a9d09ed1', InstanceType='t2.micro', MinCount=1, MaxCount=1)


if __name__ == '__main__':
    ec2 = boto3.resource('ec2')
    ec2Obj = Ec2Class()
    ec2Obj.listInstance(ec2)
    ec2Obj.createInstance(ec2)