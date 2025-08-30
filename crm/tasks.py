import logging
from celery import shared_task
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# GraphQL setup
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql/",
    verify=False,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=True)

logger = logging.getLogger(__name__)

@shared_task
def generate_crm_report():
    try:
        query = gql("""
        {
            customers { id }
            orders { id totalamount }
        }
        """)
        response = client.execute(query)

        total_customers = len(response["customers"])
        total_orders = len(response["orders"])
        total_revenue = sum(float(order["totalamount"]) for order in response["orders"])

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue"

        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(report + "\n")

        logger.info("CRM Report generated: %s", report)

    except Exception as e:
        logger.error("Error generating CRM report: %s", e)

