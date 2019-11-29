import time

class PID:

	def __init__(self, kP, kI, kD):
		self.kP = kP
		self.kI = kI
		self.kD = kD

	def initialize(self):
		self.time_prev = time.monotonic()
		self.prev_error = 0
		self.P = 0
		self.I = 0
		self.D = 0

	def update(self, error):
		# Update times and errors
		time_now = time.monotonic()
		delta_time = time_now - self.time_prev
		self.time_prev = time_now
		delta_error = error - self.prev_error
		self.prev_error = error
		# Calculate the three terms and return the sum of them
		self.P = error * self.kP
		self.I += error * delta_time * self.kI
		self.D = delta_error / delta_time * self.kD
		return self.P + self.I + self.D