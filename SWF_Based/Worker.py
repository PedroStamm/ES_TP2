import boto3
from botocore.client import Config

botoConfig = Config(connect_timeout=50, read_timeout=70)
swf = boto3.client('swf', config=botoConfig)
s3 = boto3.resource("s3")
bucket = s3.Bucket("pstammjobdata")


def fibonacci(n):
    if n <= 2:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


print "Listening for Worker Tasks"

while True:

    task = swf.poll_for_activity_task(
        domain="ESSWF",  # string
        taskList={'name': "FibTaskList"},  # TASKLIST is a string
        identity='worker')  # identity is for our history

    if 'taskToken' not in task:
        print("Poll time out")

    else:
        print("Got Fibonacci job")
        key = task['input']
        bucket.download_file(key, "/home/ec2-user/" + key)
        f = open("/home/ec2-user/" + key, 'r')
        read_str = f.read()
        n = int(read_str)
        res = fibonacci(n)
        bucket.put_object(Key=key + "_out", Body=str(res))
        swf.respond_activity_task_completed(
            taskToken=task['taskToken'],
            result='success'
        )
        print("Fibonacci job complete")
