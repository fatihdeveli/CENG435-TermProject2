from socket import *
import thread
from time import sleep
from datetime import datetime

broker_name = '10.10.1.2'
send_port = 3004
receive_port = 3000
data_list = []
message_size
ack = 0
ack_size = 64

def send():
	send_socket = socket(AF_INET, SOCK_DGRAM)
	print (len(data_list))
	while 1:
		global ack
		i = ack
		data = data_list[i]
		packet = str(i) + " " + str(data)
		send_socket.sendto(packet, (broker_name, send_port))
		#ack = i+1

def receive():
	receive_socket = socket(AF_INET, SOCK_DGRAM)
	receive_socket.bind(('', receive_port))
	print "ready"
	while 1:
		global ack
		message, broker_address = receive_socket.recvfrom(message_size)
		#print message
		ack = ack +1


def main():
	global data_list
	pck_size = 512
	window_size = 5
	with open('input.txt', 'rb') as file:
			file_data = file.read()

	file_length = len(file_data)
	data_list = [file_data[i:i+pck_size] for i in range(0, file_length, pck_size)]
	file.close()

	try:
		thread.start_new_thread(receive, ())
		thread.start_new_thread(send, ())
	except:
		print "Error: unable to start thread"
		exit()

	sleep(600)

if __name__ == '__main__':
	main()


