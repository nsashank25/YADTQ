from kafka import KafkaConsumer, KafkaProducer
import json
from redis_storage import RedisBackend
import time
import random
import threading

# Initialize Redis backend
redis_backend = RedisBackend(backend_ip='127.0.0.1')

# Kafka producer for task retries
producer = KafkaProducer(
    bootstrap_servers='127.0.0.1',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Task functions
def add(a, b):
    return a + b

def sub(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b

def process_task(task, worker_id):
    task_id = task["task-id"]
    task_type = task["task"]
    args = task["args"]
    retries = task.get("retries", 0)
    max_retries = 3

    redis_backend.set_task_status(task_id, "processing")

    try:
        # Simulate task processing time
        processing_time = random.randint(5, 10)
        time.sleep(processing_time)

        # Execute task based on type
        if task_type == "add":
            result = add(*args)
        elif task_type == "sub":
            result = sub(*args)
        elif task_type == "multiply":
            result = multiply(*args)
        elif task_type == "divide":
            result = divide(*args)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

        # Store the result and update status
        redis_backend.set_task_status(task_id, "success")
        redis_backend.set_task_result(task_id, result)
        print(f"Worker {worker_id}: Task {task_id} completed in {processing_time} seconds.")

    except Exception as e:
        if retries < max_retries:
            task["retries"] = retries + 1
            print(f"Worker {worker_id}: Task {task_id} failed. Retrying ({task['retries']}/{max_retries})...")
            redis_backend.set_task_status(task_id, "retrying")
            producer.send('tasks', task)
        else:
            redis_backend.set_task_status(task_id, "failed")
            redis_backend.set_task_result(task_id, str(e))
            print(f"Worker {worker_id}: Task {task_id} failed permanently after {max_retries} retries: {e}")

# Worker heartbeat function
def heartbeat(worker_id):
    while True:
        redis_backend.set_worker_heartbeat(worker_id)
        time.sleep(5)  # Heartbeat interval

# Start a single worker
def start_worker(worker_id, group_id):
    threading.Thread(target=heartbeat, args=(worker_id,), daemon=True).start()

    consumer = KafkaConsumer(
        'tasks',
        bootstrap_servers='127.0.0.1',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id=group_id  # Consumer group ensures each task is handled by one worker
    )

    print(f"Worker {worker_id} started. Listening for tasks...")
    for message in consumer:
        task = message.value
        process_task(task, worker_id)

if __name__ == "__main__":
    import sys
    worker_id = sys.argv[1] if len(sys.argv) > 1 else f"worker-{random.randint(1000, 9999)}"
    group_id = "task_workers"  # All workers share the same group ID
    print(f"Starting worker with ID: {worker_id} in group {group_id}")
    start_worker(worker_id, group_id)

