# pytask

A simple Python task daemon for asynchronous IO bound tasks, based on greenlets. Support for distributed/HA setups.

## Synopsis

```py
import gevent
gevent.monkey.patch_all()
import redis
from pytask import PyTask, Task, Monitor, run_loop

# Create pytask and pass it a Redis instance
task_app = PyTask(redis.StrictRedis())

# A custom task
class MyTask(Task):
    class Config:
        NAME = 'test-task'

    # Configure/prepare the task
    def __init__(self, **task_data):
        self.interval = task_data.pop('interval', 10)

    # Start the task
    def start(self):
        run_loop(self.loop, self.interval)

    # Do some work
    def loop(self):
        print 'Doing stuff...'

task_app.add_task(MyTask)
task_app.run()
```

To start tasks, set the task name and some JSON task_data to the task has and push the task_id to the queue:

```sh
redis-cli> HSET task-<task_id> task <task_name>
redis-cli> HSET task-<task_id> data <task_data>
redis-cli> LPUSH new-task <task_id>
```


## Watching & controlling tasks via Redis pub/sub

Tasks can be stopped, started & reloaded via pub/sub. Tasks can also emit events to pub/sub so progress can be watched externally:

```sh
# To control tasks
redis-cli> PUBLISH task-<task_id>-control [stop|start|reload]

# To watch tasks
redis-cli> SUBSCRIBE task-<task_id>

# To watch all tasks:
redis-cli> PSUBSCRIBE task-*
```

Task events are sent as a JSON object, with `event` and `data` keys.


## Monitoring tasks

pytask includes a task for doing this:

```py
...
from pytask import Monitor
...
task_app.add_task(Monitor)
task_app.pre_start_task('pytask/monitor')
task_app.run()
```


## Distribution/HA

pytask assumes Redis is setup in a highly-available manner; any client compatible with pyredis will work. When the connection to Redis is lost for more than 60 seconds, all tasks are stopped locally. Assuming the rest of the pytask instances have access to Redis, and one of them is running a `Monitor` task, the stopped tasks will be requeued.


## Internals

### Task data

Stored has a hash in Redis:

```py
{
    # Required to 'create' task
    'function': 'task_name',
    'data': 'json_data',
    # Internally created/used
    'last_update': 0,
    'state': '[RUNNING|ENDED|ERROR|STOPPED|WAIT]'
}
```

### Task states

+ `RUNNING` - the task is active, and to be monitoed
+ `ENDED` - the task ended successfully
+ `ERROR` - the task had an error
+ `STOPPED` - the task was intentionally stopped, no monitoring occurs
