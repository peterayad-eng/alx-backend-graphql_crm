#!/usr/bin/env python3

import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def main():
    """Main function to send order reminders"""
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )

    try:
        client = Client(transport=transport, fetch_schema_from_transport=True)
    except Exception as e:
        error_msg = f"Failed to create GraphQL client: {e}\n"
        sys.stderr.write(error_msg)
        with open("/tmp/order_reminders_log.txt", "a") as log_file:
            log_file.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} - ERROR: {error_msg}")
        sys.exit(1)

    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)

    query = gql("""
        query getRecentOrders($fromDate: Date!) {
          orders(orderDate_Gte: $fromDate) {
            id
            orderDate
            customer {
              email
              name
            }
            totalAmount
          }
        }
    """)

    try:
        result = client.execute(query, variable_values={"fromDate": str(week_ago)})
        orders = result.get("orders", [])
    except Exception as e:
        error_msg = f"GraphQL query failed: {e}\n"
        sys.stderr.write(error_msg)
        with open("/tmp/order_reminders_log.txt", "a") as log_file:
            log_file.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} - ERROR: {error_msg}")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("/tmp/order_reminders_log.txt", "a") as log_file:
        if not orders:
            log_file.write(f"{timestamp} - No recent orders found\n")
        else:
            for order in orders:
                amount = float(order.get("totalAmount", 0) or 0)
                log_entry = (
                    f"{timestamp} - Order ID: {order['id']}, "
                    f"Date: {order.get('orderDate', 'N/A')}, "
                    f"Customer: {order['customer']['name']} ({order['customer']['email']}), "
                    f"Amount: ${amount:.2f}\n"
                )
                log_file.write(log_entry)

    print("Order reminders processed!")

if __name__ == "__main__":
    main()

