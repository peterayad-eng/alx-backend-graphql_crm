import os
import django
import logging
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")
django.setup()

# Logging setup
logging.basicConfig(
    filename="/tmp/cron_jobs.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# GraphQL client setup
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql/",
    verify=True,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=True)

# ============================
# 1) Log Heartbeat
# ============================
def log_crm_heartbeat():
    """Log a heartbeat message and verify GraphQL hello endpoint."""
    now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    status = "CRM is alive"

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql("{ hello }")
        response = client.execute(query)
        status += f" | GraphQL says: {response.get('hello')}"
    except Exception as e:
        status += f" | GraphQL check failed: {e}"

    message = f"{now} {status}\n"

    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(message)

# ============================
# 2) Update Low-Stock Products
# ============================
def update_low_stock():
    mutation = gql(
        """
        mutation {
          updateLowStockProducts {
            updatedProducts {
              id
              name
              stock
            }
            message
          }
        }
        """
    )

    try:
        response = client.execute(mutation)
        updates = response["updateLowStockProducts"]["updatedProducts"]
        message = response["updateLowStockProducts"]["message"]

        log_entry = f"{datetime.now()} - {message}\n"
        for product in updates:
            log_entry += f"  • {product['name']} new stock: {product['stock']}\n"

        logging.info(log_entry)
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(log_entry + "\n")

    except Exception as e:
        err_msg = f"Error running low stock update: {e}"
        logging.error(err_msg)
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"{datetime.now()} - {err_msg}\n")

