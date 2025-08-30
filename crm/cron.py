import os
from datetime import datetime
import requests

def log_crm_heartbeat():
    """Log a heartbeat message to confirm CRM health."""
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"

    # Append message to log file
    with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
        log_file.write(log_message)

    # Ping GraphQL hello field
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.ok and "hello" in response.text:
            with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
                log_file.write(f"{timestamp} GraphQL hello OK\n")
        else:
            with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
                log_file.write(f"{timestamp} GraphQL hello FAILED\n")
    except Exception as e:
        with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
            log_file.write(f"{timestamp} GraphQL query error: {e}\n")

