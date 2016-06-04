import boto3

sqs = boto3.resource('sqs')
s3 = boto3.resource('s3')
bucket = s3.Bucket('pstammjobdata')
try:
    queue = sqs.get_queue_by_name(QueueName='in_queue')
except:
    queue = sqs.create_queue(QueueName='in_queue', Attributes={'DelaySeconds': '5'})

bucket.put_object(Key="TestString", Body="This String")

queue.send_message(
    MessageBody='PrintString',
    MessageAttributes={
        'bucket':{
            'StringValue': 'pstammjobdata',
            'DataType': 'String'
        },
        'key':{
            'StringValue': 'TestString',
            'DataType': 'String'
        }
    }
)