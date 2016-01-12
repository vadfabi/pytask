# pytask
# File: pytask/pytask.py
# Desc: the base Task instance

import json


class Task(object):
    '''An individual task base.'''

    # Internal task_id
    _id = None

    # Internal task state
    _state = 'WAIT'

    # Redis object
    _redis = None

    # & channel name
    _channel = None

    class Error(Exception):
        '''An exception which, when raised, puts this task in the ``ERROR`` state.'''
        pass

    def __init__(self, **task_data):
        pass

    # Tasks which don't define a stop are assumed not to spawn any sub-greenlets
    # this is called before we kill the task's greenlet (running task.start)
    def stop(self):
        pass

    def emit(self, event, data=None):
        '''Emit task events -> pubsub channel.'''

        self._redis.publish(self._channel, json.dumps({
            'event': event,
            'data': data
        }))
