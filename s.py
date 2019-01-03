from socket import *
from io import open
from time import sleep

def main():
	# Connection definitions
	broker_name = '10.10.1.2'
	send_port = 4009
	message_size = 500

	# Read the input file
	with open('input.txt', 'rb') as file:
		file_data = file.read()

	file_size = len(file_data)
	file.close()

	sckt = socket(AF_INET, SOCK_STREAM)
	sckt.connect((broker_name, send_port))

	# Send
	for i in range(10000):
		message = file_data[i*message_size:(i+1)*message_size]
		sckt.send(message)


if __name__ == '__main__':
	main()

