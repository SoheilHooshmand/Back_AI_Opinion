import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simulate_human_samples.settings')

app = Celery('simulate_human_samples')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'ask_gpt': {
        'task': 'project.tasks.ask_gpt',
        'schedule': crontab(minute=0, hour='*/1'),
    },
    'analysis_results': {
        'task': 'project.tasks.analysis_results',
        'schedule': crontab(minute=0, hour='*/1'),
    }
}