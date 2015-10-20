import serial
from time import sleep

class Arduino:
	"""
		Se connecter à l'arduino grace a pyserial facilement!
	"""

	def __init__(port, baud_rate, timeout=0.1):
		self.port = port
		#meme valeur que celle utilisé dans le code arduino!
		self.baud_rate = baud_rate
		self.timeout = timeout
		self.log  = []
	

	def connect(self):
		try:
			self.ard = serial.Serial(self.port, self.baud_rate, self.timeout)
			sleep(self.timeout*10)
		except serial.serialutil.SerialException:
    		self.log.append("Arduino not connected!")


    def isconnected(self):
    	try:
    		return self.ard.isOpen() and not(self.ard.iswaiting())
    	except:
    		return False

    def iswaiting(self):
    	return self.ard.inWaiting()


    def disconnect(self):
    	try:
    		self.ard.close()
    		self.log.append("Arduino disconnected!")
    	except SerialException:
    		continue


    def write(self, data):
    	if not self.iswaiting():
    		self.ard.write(data)
    	else:
    		self.log.append("Lost connection!")


    def read(self):
    	if not self.iswaiting() and self.ard.readable():
    		return self.ard.read()
    	else:
    		self.log.append("Lost connection!")


    def readline(self):
    	if not self.iswaiting() and self.ard.writable():
    		return self.readline().strip()
    	else:
    		self.log.append("Lost connection!")


   	def get_log(self):
   		if self.log:
   			return self.log
