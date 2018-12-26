from socket import *
import thread
from time import sleep
from datetime import datetime
import _strptime

# Receiving ports
r1_port = 3002
r2_port = 3003
# Sending ports
s1_port = 3005
s2_port = 3006

# Send address
s1_name = '10.10.2.1'
s2_name = '10.10.4.1'

message_size = 512

def receive_from_1():
	s1_socket = socket(AF_INET, SOCK_DGRAM)
	r1_socket = socket(AF_INET, SOCK_DGRAM)
	r1_socket.bind(('', r1_port))
	while 1:
		message, r1_address = r1_socket.recvfrom(message_size)
		print "message from r1"
		s1_socket.sendto('aldik mesaji' , (s1_name, s1_port))


def receive_from_2(): # Thread r2 communicates with router 2
	s2_socket = socket(AF_INET, SOCK_DGRAM)
	r2_socket = socket(AF_INET, SOCK_DGRAM)
	r2_socket.bind(('', r2_port))
	while 1:
		message, r2_address = r2_socket.recvfrom(message_size)
		print "message from r2:"
		s2_socket.sendto('aynn knk', (s2_name, s2_port))

def main():
	try:
		thread.start_new_thread(receive_from_1,())
		thread.start_new_thread(receive_from_2,())
		#thread.start_new_thread(send_to_1)
		#thread.start_new_thread(send_to_2)
	except:
		print "Error: unable to start thread"
		exit()
	try:
		sleep(60)
		print("End")
	except(KeyboardInterrupt):
		exit()

if __name__ == '__main__':
	main()
