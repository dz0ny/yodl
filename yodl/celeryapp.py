from __future__ import absolute_import
import os

from celery import Celery

app = Celery(
    'yodl',
    broker=os.getenv('REDISTOGO_URL', 'redis://localhost:6379'),
    backend=os.getenv('REDISTOGO_URL', 'redis://localhost:6379'),
    include=['yodl.tasks']
)

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_ACCEPT_CONTENT=['pickle', 'json'],
    CELERY_RESULT_BACKEND=os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
)

if __name__ == '__main__':
    app.start()
