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
    print("Out of polling")

    if 'taskToken' not in newTask:
        print "Poll timed out"
    elif 'events' in newTask:
        print"Got a thing"
        eventHistory = [evt for evt in newTask['events'] if not evt['eventType'].startswith('Decision')]
        lastEvent = eventHistory[-1]

        if lastEvent['eventType'] == 'WorkflowExecutionStarted':
            print "Dispatching task to worker", newTask['workflowExecution'], newTask['workflowType']
            cur_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            swf.respond_decision_task_completed(
                taskToken=newTask['taskToken'],
                decisions=[
                    {
                        'decisionType': 'ScheduleActivityTask',
                        'scheduleActivityTaskDecisionAttributes': {
                            'activityType': {
                                'name': "StoreInputS3",  # string
                                'version': "1.1"  # string
                            },
                            'activityId': 'activityid-'+cur_date,
                            'input': lastEvent['workflowExecutionStartedEventAttributes']['input'],
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
            prev_activityTas = lastEvent
            for ev in eventHistory:
                if ev['eventType'] == 'ActivityTaskScheduled':
                    prev_activityTask = ev
                    break
            prev_activityName = prev_activityTask['activityTaskScheduledAttributes']['activityType']['name']
            if prev_activityName == 'StoreInputS3':
                print "Dispatching task to worker", newTask['workflowExecution'], newTask['workflowType']
                cur_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                swf.respond_decision_task_completed(
                    taskToken=newTask['taskToken'],
                    decisions=[
                        {
                            'decisionType': 'ScheduleActivityTask',
                            'scheduleActivityTaskDecisionAttributes': {
                                'activityType': {
                                    'name': "CalculateFib",  # string
                                    'version': "1.1"  # string
                                },
                                'activityId': 'activityid-' + cur_date,
                                'input': lastEvent['activityTaskCompletedEventAttributes']['result'],
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
            elif prev_activityName == 'CalculateFib':
                print "Dispatching task to worker", newTask['workflowExecution'], newTask['workflowType']
                cur_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                swf.respond_decision_task_completed(
                    taskToken=newTask['taskToken'],
                    decisions=[
                        {
                            'decisionType': 'ScheduleActivityTask',
                            'scheduleActivityTaskDecisionAttributes': {
                                'activityType': {
                                    'name': "StoreOutputS3",  # string
                                    'version': "1.1"  # string
                                },
                                'activityId': 'activityid-' + cur_date,
                                'input': lastEvent['activityTaskCompletedEventAttributes']['result'],
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
            else:
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
