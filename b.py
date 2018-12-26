from socket import *
from datetime import datetime
from time import sleep
import thread

s_address = '10.10.1.1'
d1_address = '10.10.3.2'
d2_address = '10.10.5.2'

send_to_s_from_d1_port = 3000
send_to_s_from_d2_port = 3000
send_to_d1_port = 3002
send_to_d2_port = 3003
recv_from_s_port = 3004
recv_from_d1_port = 3005
recv_from_d2_port = 3006

message_size = 512

def receive_from_s_send_to_d():
	send_to_d1_socket = socket(AF_INET, SOCK_DGRAM)
	send_to_d2_socket = socket(AF_INET, SOCK_DGRAM)
	recv_from_s_socket = socket(AF_INET, SOCK_DGRAM)
	recv_from_s_socket.bind(('', recv_from_s_port))

	target = True;
	while 1:
		message, s_address = recv_from_s_socket.recvfrom(message_size)
		if (target):
			send_to_d1_socket.sendto(message, (d1_address, send_to_d1_port))
			target = False
		else:
			send_to_d2_socket.sendto(message, (d2_address, send_to_d2_port))
			target = True


def receive_from_d1_send_to_s():
	send_to_s_socket = socket(AF_INET, SOCK_DGRAM)
	recv_from_d1_socket = socket(AF_INET, SOCK_DGRAM)
	recv_from_d1_socket.bind(('', recv_from_d1_port))
	while 1:
		message, d1_address = recv_from_d1_socket.recvfrom(message_size)
		send_to_s_socket.sendto(message, (s_address, send_to_s_from_d1_port))
		print 'sent from d1'


def receive_from_d2_send_to_s():
	send_to_s_socket = socket(AF_INET, SOCK_DGRAM)
	recv_from_d2_socket = socket(AF_INET, SOCK_DGRAM)
	recv_from_d2_socket.bind(('', recv_from_d2_port))
	while 1:
		message, d2_address = recv_from_d2_socket.recvfrom(message_size)
		send_to_s_socket.sendto(message, (s_address, send_to_s_from_d2_port))
		print 'sent from d2'


def main():
	try:
		thread.start_new_thread(receive_from_d1_send_to_s, ())
		thread.start_new_thread(receive_from_d2_send_to_s, ())
		thread.start_new_thread(receive_from_s_send_to_d, ())
	except:
		print "Error: unable to start thread"
		exit()


	sleep(99999999)


if __name__ == '__main__':
		main()

