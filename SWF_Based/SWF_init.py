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
        version="1.0",  # string
        description="Makes a worker calculate the number",
        defaultTaskStartToCloseTimeout="NONE",
        defaultTaskList={"name": "FibTaskList"}  # TASKLIST is a string
    )
    print "Worker created!"
except ClientError as e:
    print "Activity already exists: ", e.response.get("Error", {}).get("Code")

response = swf.start_workflow_execution(
  domain="ESSWF", # string,
  workflowId='test-1001',
  workflowType={
    "name": "Fibonacci",# string
    "version": "1.0" # string
  },
  taskList={
      'name': "FibTaskList"
  },
  input='5'
)

print "Workflow requested: ", response