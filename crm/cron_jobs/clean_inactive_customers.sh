#!/bin/bash

# Go to the Django project root where manage.py is
cd /alx_backend_graphql_crm || exit 1

# Run Django shell
deleted_count=$(python3 manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

cutoff = timezone.now() - timedelta(days=365)
to_delete = Customer.objects.filter(orders__isnull=True) | Customer.objects.exclude(orders__order_date__gte=cutoff)
count = to_delete.distinct().count()
to_delete.distinct().delete()
print(count)
")

# Log results
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt

