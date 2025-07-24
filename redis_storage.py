import redis
import time

class RedisBackend:
    def __init__(self, backend_ip, port=6379, db=0):
        self.redis_client = redis.Redis(host=backend_ip, port=port, db=db)

    def set_task_status(self, task_id, status):
        self.redis_client.hset(task_id, "status", status)

    def set_task_result(self, task_id, result):
        self.redis_client.hset(task_id, "result", result)

    def get_task_status(self, task_id):
        status = self.redis_client.hget(task_id, "status")
        return status.decode('utf-8') if status else None

    def get_task_result(self, task_id):
        result = self.redis_client.hget(task_id, "result")
        return result.decode('utf-8') if result else None

    # Worker heartbeat methods
    def set_worker_heartbeat(self, worker_id):
        self.redis_client.hset("workers", worker_id, time.time())

    def get_all_workers(self):
        workers = self.redis_client.hgetall("workers")
        return {worker.decode('utf-8'): float(timestamp) for worker, timestamp in workers.items()}

