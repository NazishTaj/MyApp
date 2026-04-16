import os
import django
import csv

# 🔥 Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowdesk.settings")
django.setup()

from core.models import Medicine

file_path = "MedList.csv"

meds = []
BATCH_SIZE = 500

print("🚀 Import started...")

with open(file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)

    # ⚠️ agar CSV me header hai to uncomment kar
    # next(reader)

    for i, row in enumerate(reader):
        try:
            name = row[0].strip()
        except:
            continue

        if not name:
            continue

        meds.append(Medicine(name=name, clinic=None))  # 🔥 global meds

        if len(meds) >= BATCH_SIZE:
            Medicine.objects.bulk_create(meds, ignore_conflicts=True)
            print(f"Inserted {i} medicines...")
            meds = []

# remaining
if meds:
    Medicine.objects.bulk_create(meds, ignore_conflicts=True)

print("✅ DONE 🚀")
