import datetime
import boto3
from botocore.exceptions import ClientError

swf = boto3.client('swf')
try:
    swf.register_domain(
        name="ESSWF",
        description="Test SWF domain",
        workflowExecutionRetentionPeriodInDays="10"  # keep history for this long
    )
except ClientError as e:
    print "Domain already exists: ", e.response.get("Error", {}).get("Code")

try:
    swf.register_workflow_type(
        domain="ESSWF",  # string
        name="Fibonacci",  # string
        version="1.0",  # string
        description="Calculate Fibonacci number",
        defaultExecutionStartToCloseTimeout="300",
        defaultTaskStartToCloseTimeout="NONE",
        defaultChildPolicy="TERMINATE",
        defaultTaskList={"name": "FibTaskList"}  # TASKLIST is a string
    )
    print "Test workflow created!"
except ClientError as e:
    print "Workflow already exists: ", e.response.get("Error", {}).get("Code")

try:
    swf.register_activity_type(
        domain="ESSWF",
        name="CalculateFib",
        version="1.1",  # string
        description="Makes a worker calculate the number",
        defaultTaskStartToCloseTimeout="NONE",
        defaultTaskList={"name": "FibTaskList"}  # TASKLIST is a string
    )
    print "Worker created!"
except ClientError as e:
    print "Activity already exists: ", e.response.get("Error", {}).get("Code")

try:
    swf.register_activity_type(
        domain="ESSWF",
        name="StoreInputS3",
        version="1.0",  # string
        description="Makes a worker save input on S3",
        defaultTaskStartToCloseTimeout="NONE",
        defaultTaskList={"name": "FibTaskList"}  # TASKLIST is a string
    )
    print "Worker created!"
except ClientError as e:
    print "Activity already exists: ", e.response.get("Error", {}).get("Code")

try:
    swf.register_activity_type(
        domain="ESSWF",
        name="StoreOutputS3",
        version="1.0",  # string
        description="Makes a worker save input on S3",
        defaultTaskStartToCloseTimeout="NONE",
        defaultTaskList={"name": "FibTaskList"}  # TASKLIST is a string
    )
    print "Worker created!"
except ClientError as e:
    print "Activity already exists: ", e.response.get("Error", {}).get("Code")

cur_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
response = swf.start_workflow_execution(
    domain="ESSWF",  # string,
    workflowId=cur_date,
    workflowType={
        "name": "Fibonacci",  # string
        "version": "1.0"  # string
    },
    taskList={
        'name': "FibTaskList"
    },
    input='5'
)

print "Workflow requested: ", response
