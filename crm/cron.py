import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """Log a heartbeat message and verify GraphQL hello endpoint."""
    now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
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

