from yadtq import YADTQ
import time

yadtq = YADTQ(broker_ip='127.0.0.1', backend_ip='127.0.0.1')
while True:
	yadtq.display_worker_status()
	time.sleep(5)