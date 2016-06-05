# coding=utf-8
"""
Made by Pedro Stamm
For Services Engineering Course
Departamento de Engenharia Informática
Faculdade de Ciências de Tecnologia
Universidade de Coimbra
"""

import boto3

sqs = boto3.resource('sqs')
s3 = boto3.resource('s3')

try:
    queue = sqs.get_queue_by_name(QueueName='out_queue')
except:
    queue = sqs.create_queue(QueueName='out_queue', Attributes={'DelaySeconds': '5'})

for message in queue.receive_messages(MaxNumberOfMessages=10, MessageAttributeNames=['key', 'bucket']):
    if message.body == 'Fibonacci_res':
        key = message.message_attributes.get('key').get('StringValue')
        bucket_name = message.message_attributes.get('bucket').get('StringValue')
        bucket = s3.Bucket(bucket_name)
        bucket.download_file(key, 'tmp/'+key)
        f=open('tmp/'+key, 'r')
        str = f.read()
        print("Got Job Result: "+message.body)
        print("Data received: "+str)
        message.delete()
        for object in bucket.objects.filter(Prefix=key):
            if object.key == key:
                object.delete()
    elif message.body == 'PrintString_res':
        key = message.message_attributes.get('key').get('StringValue')
        bucket_name = message.message_attributes.get('bucket').get('StringValue')
        bucket = s3.Bucket(bucket_name)
        bucket.download_file(key, 'tmp/'+key)
        f=open('tmp/'+key, 'r')
        str = f.read()
        print("Got Job Result: "+message.body)
        print("Data received: "+str)
        message.delete()
        for object in bucket.objects.filter(Prefix=key):
            if object.key == key:
                object.delete()
    else:
        print("Got Message: "+message.body)
