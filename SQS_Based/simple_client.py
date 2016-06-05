import boto3
import datetime
sqs = boto3.resource('sqs')
in_queue = sqs.get_queue_by_name(QueueName='in_queue')
out_queue = sqs.get_queue_by_name(QueueName='out_queue')

s3 = boto3.resource('s3')
bucket = s3.Bucket("pstammjobdata")

exit_loop = False

while exit_loop is False:
    user_in = raw_input("Command:\n>")
    if user_in == "exit":
        exit_loop = True
    elif user_in == "fibonacci":
        user_in = raw_input("Number to calculate:\n>")
        bucket.put_object(Key=datetime.datetime.now().strftime("%Y%m%d%H%M%S"), Body=user_in)
        in_queue.send_message(
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
        print("Fibonacci job sent")
    elif user_in == "print_string":
        user_in = raw_input("String to send:\n>")
        in_queue.send_message(
            MessageBody='PrintString',
            MessageAttributes={
                'bucket': {
                    'StringValue': 'pstammjobdata',
                    'DataType': 'String'
                },
                'key': {
                    'StringValue': 'TestString',
                    'DataType': 'String'
                }
            }
        )
        bucket.put_object(Key="TestString", Body=user_in)
        print("Print String job sent")
    elif user_in == "worker_status":
        autoscale = boto3.client('autoscaling')
        for group in autoscale.AutoScalingGroups:
            print("Group Name: "+group.AutoScalingGroupName)
            print("Launch Configuration: "+group.LaunchConfigurationName)
            print("Min Size: "+group.MinSize)
            print("Max Size: "+group.MaxSize)
            print("Initial Instances: "+group.DesiredCapacity)
            print("Created in: "+group.CreatedTime.strftime("%d/%m/%Y"))
            print("Instances: ")
            for instance in group.Instances:
                print("Instance ID: "+instance.InstanceID)
                print("Zone: "+instance.AvailabilityZone)
                print("Status: "+instance.HealthStatus)

