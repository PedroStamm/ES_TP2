import boto3
import datetime
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

    elif task['activityType']['name'] == 'CalculateFib':
        print("Got Fibonacci job")
        key = task['input']
        # "/home/ec2-user/" +
        bucket.download_file("swf/" + key, key)
        f = open(key, 'r')
        read_str = f.read()
        n = int(read_str)
        res = fibonacci(n)
        bucket.put_object(Key=key + "_out", Body=str(res))
        swf.respond_activity_task_completed(
            taskToken=task['taskToken'],
            result=str(res)
        )
        for object in bucket.objects.filter(Prefix="swf/" + key):
            if object.key == key:
                object.delete()
        print("Fibonacci job complete")
    elif task['activityType']['name'] == 'StoreInputS3':
        print("Got store input job")
        value = task['input']
        cur_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        bucket.put_object(Key="swf/" + cur_date, Body=value)
        swf.respond_activity_task_completed(
            taskToken=task['taskToken'],
            result=cur_date
        )
    elif task['activityType']['name'] == 'StoreOutputS3':
        print("Got store output job")
        value = task['input']
        cur_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        bucket.put_object(Key="swf_out/" + cur_date, Body=value)
        swf.respond_activity_task_completed(
            taskToken=task['taskToken'],
            result=cur_date
        )
