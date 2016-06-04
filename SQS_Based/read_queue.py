import boto3

sqs = boto3.resource('sqs')

try:
    queue = sqs.get_queue_by_name(QueueName='out_queue')
except:
    queue = sqs.create_queue(QueueName='out_queue', Attributes={'DelaySeconds': '5'})

for message in queue.receive_messages(MaxNumberOfMessages=10):
    print(message.message_id+": "+message.body)
    message.delete()