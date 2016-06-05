import boto3
import datetime

swf = boto3.client("swf")
s3 = boto3.resource("s3")
bucket = s3.Bucket("pstammjobdata")

print "Listening for Decision Task"

while True:
    newTask = swf.poll_for_decision_task(
        domain="ESSWF",
        taskList={'name': "FibTaskList"},
        identity='decider-1',
        reverseOrder=False
    )

    if 'taskToken' not in newTask:
        print "Poll timed out"
    elif 'events' in newTask:
        eventHistory = [evt for evt in newTask['events'] if not evt['eventType'].startswith('Decision')]
        lastEvent = eventHistory[-1]

        if lastEvent['eventType'] == 'WorkflowExecutionStarted':
            print "Dispatching task to worker", newTask['workflowExecution'], newTask['workflowType']
            cur_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            bucket.put_object(Key="swf/"+cur_date, Body=lastEvent['workflowExecutionStartedEventAttributes']['input'])
            swf.respond_decision_task_completed(
                taskToken=newTask['taskToken'],
                decisions=[
                    {
                        'decisionType': 'ScheduleActivityTask',
                        'scheduleActivityTaskDecisionAttributes': {
                            'activityType': {
                                'name': "CalculateFib",  # string
                                'version': "1.0"  # string
                            },
                            'activityId': 'activityid-'+cur_date,
                            'input': cur_date,
                            'scheduleToCloseTimeout': 'NONE',
                            'scheduleToStartTimeout': 'NONE',
                            'startToCloseTimeout': 'NONE',
                            'heartbeatTimeout': 'NONE',
                            'taskList': {'name': "FibTaskList"},  # TASKLIST is a string
                        }
                    }
                ]
            )
            print "Task Dispatched:", newTask['taskToken']

        elif lastEvent['eventType'] == 'ActivityTaskCompleted':
            swf.respond_decision_task_completed(
                taskToken=newTask['taskToken'],
                decisions=[
                    {
                        'decisionType': 'CompleteWorkflowExecution',
                        'completeWorkflowExecutionDecisionAttributes': {
                            'result': 'success'
                        }
                    }
                ]
            )
            print "Task Completed!"
