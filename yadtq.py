import uuid
import json
import time
from kafka import KafkaProducer
from redis_storage import RedisBackend

class YADTQ:
    def __init__(self, broker_ip, backend_ip):
        self.producer = KafkaProducer(bootstrap_servers=broker_ip, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        self.redis_backend = RedisBackend(backend_ip)

    def send_task(self, task_type, args):
        task_id = str(uuid.uuid4())
        task = {"task-id": task_id, "task": task_type, "args": args, "retries": 0}

        self.redis_backend.set_task_status(task_id, "queued")
        self.producer.send('tasks', task)

        return task_id

    def status(self, task_id):
        return self.redis_backend.get_task_status(task_id)

    def value(self, task_id):
        return self.redis_backend.get_task_result(task_id)

    def get_worker_status(self):
        """Retrieve the status of workers based on their heartbeats."""
        workers = self.redis_backend.get_all_workers()
        worker_status = {}
        current_time = time.time()

        for worker_id, last_heartbeat in workers.items():
            # Check if the heartbeat is within the acceptable time window (e.g., 15 seconds)
            if current_time - last_heartbeat < 15:
                worker_status[worker_id] = "alive"
            else:
                worker_status[worker_id] = "unresponsive"

        return worker_status

    def display_worker_status(self):
        worker_status = self.get_worker_status()
        workers = self.redis_backend.get_all_workers()

        print("Worker Statuses:")
        print(f"{'Worker ID':<20}{'Status':<15}{'Last Heartbeat'}")
        print("-" * 50)
        
        for worker_id, status in worker_status.items():
            last_heartbeat = time.strftime(
                "%Y-%m-%d %H:%M:%S", 
                time.localtime(workers[worker_id])
            )
            print(f"{worker_id:<20}{status:<15}{last_heartbeat}")

