import boto3
import datetime

sqs = boto3.resource('sqs')
s3 = boto3.resource('s3')
bucket = s3.Bucket('pstammjobdata')
try:
    queue = sqs.get_queue_by_name(QueueName='in_queue')
except:
    queue = sqs.create_queue(QueueName='in_queue', Attributes={'DelaySeconds': '5'})

# queue.send_message(MessageBody='exit')
"""
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
bucket.put_object(Key="TestString", Body="This String")
"""

queue.send_message(
    MessageBody='Fibonacci',
    MessageAttributes={
        'bucket': {
            'StringValue': 'pstammjobdata',
            'DataType': 'String'
        },
        'key': {
            'StringValue': datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            'DataType': 'String'
        }
    }
)
bucket.put_object(Key=datetime.datetime.now().strftime("%Y%m%d%H%M%S"), Body="25")
