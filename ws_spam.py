import os
import django
import time

# 🔥 PROJECT NAME = flowdesk
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowdesk.settings")
django.setup()

from core.views import send_ws_update_safe   # app = core

CLINIC_ID = 1   # change if needed

for i in range(100):
    send_ws_update_safe(CLINIC_ID, {
        "type": "test",
        "i": i
    })
    time.sleep(0.2)   # 5 events/sec
