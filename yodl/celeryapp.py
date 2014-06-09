from __future__ import absolute_import

from celery import Celery

app = Celery(
    'yodl',
    broker='redis://localhost',
    backend='redis://localhost',
    include=['yodl.tasks']
)

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_ACCEPT_CONTENT=['pickle', 'json'],
    CELERY_RESULT_BACKEND='redis://localhost/1'
)

if __name__ == '__main__':
    app.start()
