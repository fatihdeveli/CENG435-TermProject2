from socket import *
import thread
from time import sleep
from datetime import datetime
import _strptime
import hashlib
import pickle

# Receiving ports
r1_port = 3027
r2_port = 3028
# Sending ports
s1_port = 3020
s2_port = 3021

# Send address
s1_name = '10.10.2.1'
s2_name = '10.10.4.1'

message_size = 512

result_list = [None] * 5000
last_successful = -1

def receive_from_1():
	global last_successful
	global result_list
	s1_socket = socket(AF_INET, SOCK_DGRAM)
	r1_socket = socket(AF_INET, SOCK_DGRAM)
	r1_socket.bind(('', r1_port))
	while 1:
		received_list = []
		message, r1_address = r1_socket.recvfrom(message_size)
		#print "message: " + message
		message_to_send = [] # Ack
		try:
			received_list = pickle.loads(message)
			received_checksum = received_list.pop()
			calculated_checksum = hashlib.md5()
			calculated_checksum.update(pickle.dumps(received_list))

			if (received_checksum == calculated_checksum.digest()): # OK
				print "received message is OK"
				# received_list[0] -> received seqnum
				# received_list[1] -> received data
				print "placed message to " + str(received_list[0])
				result_list[received_list[0]] = received_list[1]
				i = last_successful+1
 				while 1:
					if (result_list[i] == None):
						message_to_send.append(i)
						last_successful = i-1
						break
					i = i+1
			else: # Corrupted message
				print "received corrupted message"
				message_to_send.append(last_successful+1)
		except:
			print "will send ack last suc+1: "  + str(last_successful+1)
			message_to_send.append(last_successful+1)

		try:
			# Calculate checksum for ack
			print "sending ack " + str(message_to_send[0])
			checksum = hashlib.md5()
			checksum.update(pickle.dumps(message_to_send))
			message_to_send.append(checksum.digest())
			s1_socket.sendto(pickle.dumps(message_to_send) , (s1_name, s1_port))
		except:
			print "Error calculating checksum for ack"
			exit()


def receive_from_2(): # Thread r2 communicates with router 2

	s2_socket = socket(AF_INET, SOCK_DGRAM)
	r2_socket = socket(AF_INET, SOCK_DGRAM)
	r2_socket.bind(('', r2_port))
	while 1:
		message, r2_address = r2_socket.recvfrom(message_size)
		#print "message from r2:"
		#s2_socket.sendto('aynn knk', (s2_name, s2_port))

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
		st = ''
		for e in result_list:
			if e == None:
				break
			st = st + str(e)
		with open('bitanedosya', 'w') as bit:
			bit.write(st)
	except(KeyboardInterrupt):
		exit()


if __name__ == '__main__':
	main()
