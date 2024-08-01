from app import app
import asyncio
from app.database_operations import DatabaseOperations, background_task
if __name__ == '__main__':
    database_operations = DatabaseOperations()
    concurrent_messages_threshold = 10
    check_interval = 60
    task = asyncio.get_event_loop()
    task.create_task(background_task(database_operations, concurrent_messages_threshold, check_interval))
    app.run(host='0.0.0.0', port=3000)