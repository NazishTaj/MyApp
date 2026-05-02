import os
import django
import time
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowdesk.settings")
django.setup()

from core.views import send_ws_update_safe

CLINIC_ID = 1

for i in range(30):  # total actions
    send_ws_update_safe(CLINIC_ID, {
        "type": "real_action",
        "i": i
    })
    time.sleep(1)
