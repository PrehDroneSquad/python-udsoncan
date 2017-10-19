from udsoncan import Connection, Request, Response
from udsoncan.exceptions import *
import queue

class StubbedConnection(object):
	def __init__(self):
		self.fromuserqueue = queue.Queue()
		self.touserqueue = queue.Queue()
		self.opened = False

	def open(self):
		self.opened = True
		return self

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.close()

	def is_open(self):
		return self.opened 

	def close(self):
		self.empty_rxqueue()
		self.empty_txqueue()

		self.opened = False

	def send(self, obj):
		if isinstance(obj, Request) or isinstance(obj, Response):
			payload = obj.get_payload()  
		else :
			payload = obj

		if len(payload) > 4095:
			payload = payload[0:4095]

		self.touserqueue.put(payload)

	def wait_frame(self, timeout=2, exception=False):
		if not self.opened:
			if exception:
				raise RuntimeException("Connection is not opened")
			else:
				return None

		timedout = False
		frame = None
		try:
			frame = self.fromuserqueue.get(block=True, timeout=timeout)

		except queue.Empty:
			timedout = True
			
		if exception and timedout:
			raise TimeoutException("Did not received frame from user in time (timeout=%s sec)" % timeout)

		if frame is not None and len(frame) > 4095:
			frame = frame[0:4095]

		return frame

	def empty_rxqueue(self):
		while not self.fromuserqueue.empty():
			self.fromuserqueue.get()

	def empty_txqueue(self):
		while not self.touserqueue.empty():
			self.touserqueue.get()
