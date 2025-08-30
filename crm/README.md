# Celery Setup for CRM Reports

## Prerequisites

1. **Install Redis:**
   ```bash
   sudo apt-get install redis-server
   sudo systemctl enable redis-server
   sudo systemctl start redis-server

   # Verify Redis is running
   redis-cli ping  # Should return "PONG"
   ```

