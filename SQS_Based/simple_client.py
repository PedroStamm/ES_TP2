# coding=utf-8
"""
Made by Pedro Stamm
For Services Engineering Course
Departamento de Engenharia Informática
Faculdade de Ciências de Tecnologia
Universidade de Coimbra
"""

import boto3
import datetime
sqs = boto3.resource('sqs')
in_queue = sqs.get_queue_by_name(QueueName='in_queue')
out_queue = sqs.get_queue_by_name(QueueName='out_queue')

s3 = boto3.resource('s3')
bucket = s3.Bucket("pstammjobdata")

sdb = boto3.client('sdb')

exit_loop = False

while exit_loop is False:
    user_in = raw_input("Command:\n>")
    if user_in == "exit":
        exit_loop = True
    elif user_in == "fibonacci":
        user_in = raw_input("Number to calculate:\n>")
        cur_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        bucket.put_object(Key=cur_date, Body=user_in)
        in_queue.send_message(
            MessageBody='Fibonacci',
            MessageAttributes={
                'bucket': {
                    'StringValue': 'pstammjobdata',
                    'DataType': 'String'
                },
                'key': {
                    'StringValue': cur_date,
                    'DataType': 'String'
                }
            }
        )
        print("Fibonacci job sent")
        sdb.put_attributes(DomainName='jobdata',
                           ItemName=cur_date,
                           Attributes=[
                               {
                                   'Name': 'JobDesignation',
                                   'Value': 'Fibonacci'
                               },
                               {
                                   'Name': 'JobStatus',
                                   'Value': 'Pending'
                               }
                           ])
    elif user_in == "print_string":
        user_in = raw_input("String to send:\n>")
        cur_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        in_queue.send_message(
            MessageBody='PrintString',
            MessageAttributes={
                'bucket': {
                    'StringValue': 'pstammjobdata',
                    'DataType': 'String'
                },
                'key': {
                    'StringValue': cur_date,
                    'DataType': 'String'
                }
            }
        )
        bucket.put_object(Key=cur_date, Body=user_in)
        print("Print String job sent")
        sdb.put_attributes(DomainName='jobdata',
                           ItemName=cur_date,
                           Attributes=[
                               {
                                   'Name': 'JobDesignation',
                                   'Value': 'PrintString'
                               },
                               {
                                   'Name': 'JobStatus',
                                   'Value': 'Pending'
                               }
                           ])
    elif user_in == "get_result":
        for message in out_queue.receive_messages(MaxNumberOfMessages=10, MessageAttributeNames=['key', 'bucket']):
            print("Got Job Result")
            if message.body == 'Fibonacci_res':
                key = message.message_attributes.get('key').get('StringValue')
                bucket_name = message.message_attributes.get('bucket').get('StringValue')
                bucket.download_file(bucket_name, 'tmp/' + bucket_name)
                f = open('tmp/' + bucket_name, 'r')
                str_in = f.read()
                print("\tID: " + key + "\n\tBody: " + message.body)
                print("\tFibonacci Number: " + str_in)
                message.delete()
                for object in bucket.objects.filter(Prefix=bucket_name):
                    if object.key == bucket_name:
                        object.delete()
            elif message.body == 'PrintString_res':
                key = message.message_attributes.get('key').get('StringValue')
                bucket_name = message.message_attributes.get('bucket').get('StringValue')
                bucket.download_file(bucket_name, 'tmp/' + bucket_name)
                f = open('tmp/' + bucket_name, 'r')
                str_in = f.read()
                print("\tID: " + key + "\n\tBody: " + message.body)
                print("\tString received: " + str_in)
                message.delete()
                for object in bucket.objects.filter(Prefix=bucket_name):
                    if object.key == bucket_name:
                        object.delete()
            else:
                print("Got Message: " + message.body)
                message.delete()
    elif user_in == "job_status":
        res = sdb.select(SelectExpression='select * from jobdata')
        if 'Items' in res:
            for i in res['Items']:
                print("Job "+i['Name'])
                for r in i['Attributes']:
                    print("\t"+r['Name']+": "+r['Value'])
    elif user_in == "job_record_delete":
        user_in = raw_input("Job ID\n>")
        try:
            sdb.delete_attributes(DomainName='jobdata', ItemName=user_in)
        except:
            print("Failure in deleting job entry. Does the job exist?")
    elif user_in == "worker_status":
        autoscale = boto3.client('autoscaling')
        for group in autoscale.describe_auto_scaling_groups()['AutoScalingGroups']:
            print("Group Name: "+group['AutoScalingGroupName'])
            print("Launch Configuration: "+group['LaunchConfigurationName'])
            print("Min Size: "+str(group['MinSize']))
            print("Max Size: "+str(group['MaxSize']))
            print("Initial Instances: "+str(group['DesiredCapacity']))
            print("Created in: "+group['CreatedTime'].strftime("%d/%m/%Y"))
            print("Instances: ")
            for instance in group['Instances']:
                print("\tInstance ID: "+instance['InstanceId'])
                print("\t\tZone: "+instance['AvailabilityZone'])
                print("\t\tStatus: "+instance['HealthStatus'])
print("Closing Client")