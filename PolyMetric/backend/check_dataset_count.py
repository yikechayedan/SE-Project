import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PolyMetric.settings")
django.setup()

from apps.datasets.models import Dataset

count = Dataset.objects.count()
print(f"Total datasets in database: {count}")

datasets = Dataset.objects.all().values('id', 'name', 'status', 'creator__username', 'is_public')
for d in datasets:
    print(d)
