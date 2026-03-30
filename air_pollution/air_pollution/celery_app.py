import os
from pathlib import Path
from celery import Celery
import environ
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(env_file=os.path.join(BASE_DIR, ".env"))
# print("HOME BASE_DIR=" + str(BASE_DIR))

envType = os.environ.get("env", "dev")
# print("HOME BASE_DIR env=" + str(envType))) 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'air_pollution.settings')

app = Celery('air_pollution')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks([
    'air_pollution_be.realtime',
    # Thêm module mới ở đây, ví dụ:
    # 'air_pollution_be.analytics',
    # 'air_pollution_be.notification',
])