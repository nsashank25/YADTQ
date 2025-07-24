# YADTQ - Yet Another Distributed Task Queue

A lightweight, distributed task queue system built with Python, Kafka, and Redis. YADTQ allows you to distribute computational tasks across multiple workers with automatic retry mechanisms, task monitoring, and worker health tracking.

## Features

- **Distributed Processing**: Scale horizontally by adding more workers
- **Automatic Retries**: Failed tasks are automatically retried up to 3 times
- **Worker Health Monitoring**: Real-time worker status tracking with heartbeat mechanism
- **Task Status Tracking**: Monitor task progress from queued to completion
- **Multiple Task Types**: Built-in support for mathematical operations (add, subtract, multiply, divide)
- **Interactive Terminal GUI**: User-friendly interface for task management
- **Fault Tolerance**: Robust error handling and task failure management

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│   Kafka     │───▶│   Workers   │
│             │    │  (Broker)   │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                                      │
       │            ┌─────────────┐          │
       └───────────▶│   Redis     │◀─────────┘
                    │ (Backend)   │
                    └─────────────┘
```

- **Kafka**: Message broker for task distribution
- **Redis**: Backend storage for task status, results, and worker heartbeats
- **Workers**: Process tasks and report status
- **Client**: Submit tasks and monitor progress

## Prerequisites

- Python 3.7+
- Apache Kafka
- Redis
- Required Python packages:
  ```bash
  pip install kafka-python redis
  ```

## Quick Start

### 1. Start Workers

Start one or more workers to process tasks:

```bash
# Start worker with default ID
python worker_code.py

# Start worker with custom ID
python worker_code.py worker-001
```

### 2. Monitor Worker Health

Track worker status in real-time:

```bash
python heartbeat_monitor.py
```

### 3. Submit Tasks

#### Using the Interactive GUI:
```bash
python client_code.py
```

#### Using Python API:
```python
from yadtq import YADTQ

# Initialize YADTQ
yadtq = YADTQ(broker_ip='127.0.0.1', backend_ip='127.0.0.1')

# Submit a task
task_id = yadtq.send_task('add', [10, 20])

# Check task status
status = yadtq.status(task_id)
print(f"Task status: {status}")

# Get result (when completed)
if status == 'success':
    result = yadtq.value(task_id)
    print(f"Result: {result}")
```

## Core Components

### YADTQ Class (`yadtq.py`)
Main interface for task submission and monitoring:
- `send_task(task_type, args)`: Submit a new task
- `status(task_id)`: Get task status
- `value(task_id)`: Get task result
- `get_worker_status()`: Get worker health information

### Worker (`worker_code.py`)
Processes tasks from the Kafka queue:
- Supports task types: `add`, `sub`, `multiply`, `divide`
- Automatic retry mechanism (up to 3 attempts)
- Heartbeat reporting every 5 seconds
- Configurable processing time simulation

### Redis Backend (`redis_storage.py`)
Handles persistent storage:
- Task status and results
- Worker heartbeat tracking
- Thread-safe operations

### Terminal GUI (`client_code.py`)
Interactive interface for:
- Adding new tasks
- Viewing task status and results
- Real-time updates

## Task Status Flow

```
queued → processing → success/failed
   ↓
retrying (on failure, up to 3 times)
   ↓
failed (after max retries)
```

## Supported Task Types

| Task Type | Description | Example Args |
|-----------|-------------|--------------|
| `add` | Addition | `[5, 3]` → `8` |
| `sub` | Subtraction | `[10, 4]` → `6` |
| `multiply` | Multiplication | `[6, 7]` → `42` |
| `divide` | Division | `[15, 3]` → `5.0` |

## Configuration

### Default Settings
- **Kafka Broker**: `127.0.0.1:9092`
- **Redis Backend**: `127.0.0.1:6379`
- **Max Retries**: 3
- **Heartbeat Interval**: 5 seconds
- **Worker Timeout**: 15 seconds


## Monitoring 

### Worker Status
Use `heartbeat_monitor.py` to monitor worker health:
- **alive**: Worker is responding normally
- **unresponsive**: Worker hasn't sent heartbeat in >15 seconds

### Task Monitoring
Track tasks through the client GUI or programmatically:
```python
# Get all worker status
worker_status = yadtq.get_worker_status()
print(worker_status)

# Display formatted worker information
yadtq.display_worker_status()
```

## Scaling

### Adding Workers
Simply start additional worker processes:
```bash
python worker_code.py worker-002
python worker_code.py worker-003
# ... and so on
```

### Load Balancing
Kafka automatically distributes tasks among available workers in the same consumer group.

## Error Handling

- **Task Failures**: Automatic retry up to 3 times
- **Worker Failures**: Tasks are redistributed to healthy workers
- **Network Issues**: Built-in Kafka and Redis connection handling
- **Invalid Tasks**: Proper error messages and status updates

## Example Usage

See `tasks.json` for sample task definitions. You can bulk-load tasks:

```python
import json
from yadtq import YADTQ

yadtq = YADTQ(broker_ip='127.0.0.1', backend_ip='127.0.0.1')

# Load tasks from JSON
with open('tasks.json', 'r') as f:
    tasks = json.load(f)

# Submit all tasks
task_ids = []
for task in tasks:
    task_id = yadtq.send_task(task['task'], task['args'])
    task_ids.append(task_id)
    print(f"Submitted task {task_id}: {task['task']}({task['args']})")
```