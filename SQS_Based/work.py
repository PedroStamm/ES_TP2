import boto3


def fibonacci(n):
    if n <= 2:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


sqs = boto3.resource('sqs')
in_queue = sqs.get_queue_by_name(QueueName='in_queue')
out_queue = sqs.get_queue_by_name(QueueName='out_queue')

s3 = boto3.resource('s3')
bucket = s3.Bucket('pstammjobdata')

sdb = boto3.client('sdb')

exit = False

while exit is False:
    for message in in_queue.receive_messages(WaitTimeSeconds=20, MessageAttributeNames=['key', 'bucket']):
        if message.body == 'exit':
            exit = True
            message.delete()
        elif message.body == 'Fibonacci':
            print("Got Fibonacci job")
            key = message.message_attributes.get('key').get('StringValue')
            bucket.download_file(key, "/home/ec2-user/" + key)
            f = open("/home/ec2-user/" + key, 'r')
            read_str = f.read()
            n = int(read_str)
            sdb.put_attributes(DomainName='jobdata',
                               ItemName=key,
                               Attributes=[
                                   {
                                       'Name': 'JobDesignation',
                                       'Value': message.body
                                   },
                                   {
                                       'Name': 'JobStatus',
                                       'Value': 'Processing'
                                   }
                               ])
            res = fibonacci(n)
            out_queue.send_message(
                MessageBody=message.body + "_res",
                MessageAttributes={
                    'bucket': {
                        'StringValue': key+"_out",
                        'DataType': 'String'
                    },
                    'key': {
                        'StringValue': key,
                        'DataType': 'String'
                    }
                }
            )
            bucket.put_object(Key=key + "_out", Body=str(res))
            message.delete()
            for object in bucket.objects.filter(Prefix=key):
                if object.key == key:
                    object.delete()
            print("Fibonacci job complete")
            sdb.put_attributes(DomainName='jobdata',
                               ItemName=key,
                               Attributes=[
                                   {
                                       'Name': 'JobDesignation',
                                       'Value': message.body
                                   },
                                   {
                                       'Name': 'JobStatus',
                                       'Value': 'Complete'
                                   }
                               ])
        elif message.body == 'PrintString':
            print("Got Print job")
            key = message.message_attributes.get('key').get('StringValue')
            sdb.put_attributes(DomainName='jobdata',
                               ItemName=key,
                               Attributes=[
                                   {
                                       'Name': 'JobDesignation',
                                       'Value': message.body
                                   },
                                   {
                                       'Name': 'JobStatus',
                                       'Value': 'Processing'
                                   }
                               ])
            bucket.download_file(key, key)
            f = open(key, 'r')
            read_str = f.read()
            out_queue.send_message(
                MessageBody=message.body + "_res",
                MessageAttributes={
                    'bucket': {
                        'StringValue': key+"_out",
                        'DataType': 'String'
                    },
                    'key': {
                        'StringValue': key,
                        'DataType': 'String'
                    }
                }
            )
            bucket.put_object(Key=key + "_out", Body=read_str)
            message.delete()
            for object in bucket.objects.filter(Prefix=key):
                if object.key == key:
                    object.delete()
            print("Print job complete")
            sdb.put_attributes(DomainName='jobdata',
                               ItemName=key,
                               Attributes=[
                                   {
                                       'Name': 'JobDesignation',
                                       'Value': message.body
                                   },
                                   {
                                       'Name': 'JobStatus',
                                       'Value': 'Complete'
                                   }
                               ])
        else:
            print("Sending message " + message.message_id + ": " + message.body)
            out_queue.send_message(MessageBody=message.body)
            message.delete()
print("Left loop and done")
