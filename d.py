from socket import *
import thread
from time import sleep
from datetime import datetime
import sys

# Receiving ports
r1_port = 4007
r2_port = 4008
# Sending ports
s1_port = 4000
s2_port = 4000

# Send addresses
s1_name = '10.10.2.1'
s2_name = '10.10.4.1'

# Payload is 500 bytes, 5 bytes of packet number and one byte checksum
# is added, total size is 506 bytes.
message_size = 506

# Keep the file transfer time
starting_time = None

# Number of packets arrived (excluding duplicates)
packets_received_1 = 0 # From route 1
packets_received_2 = 0 # From route 2

# Create a list to store incoming data
result_list = [None] * 10001
last_successful_ack = -1 # Last sequence number received successfully.

def checksum(msg):
	'''
	Function calculates the checksum of the given message.
	Returns a byte.
	Works like a hash function with mod 256 operation.
	Mod operand should be 256 so that it will produce a one-byte
	result.
	'''
	chksum = 0
	for byte in bytes(msg):
		chksum = chksum + ord(byte)
	chksum = chksum % 256
	chksum = chr(chksum) # Convert to byte
	return chksum

def packetize(seqnum, data):
	'''
	Function creates a packet with given sequence number and byte
	stream data.
	First 5 characters of the packet represent the sequence number,
	and the last byte is the checksum.
	'''
	# Create 5 character long string out of seqnum.
	seqnum = str(seqnum)
	while len(seqnum) < 5:
		seqnum = '0' + seqnum
	packet = seqnum + data # Combine
	# Calculate checksum
	packet = packet + checksum(packet)
	return packet


def receive_from_1(): # Thread 1 communicates through router 1
	global last_successful_ack
	global packets_received_1

	s1_socket = socket(AF_INET, SOCK_DGRAM)
	r1_socket = socket(AF_INET, SOCK_DGRAM)
	r1_socket.bind(('', r1_port))
	while 1:
		message = bytearray(message_size)
		r1_socket.recv_into(message)
		received_checksum = ord(chr(message[-1]))
		seqnum = int(message[:5]) # Sequence number of the message
		# Delete checksum field to calculate own checksum
		message = message[:len(message)-1]
		# Calculate own checksum
		calculated_checksum = ord(checksum(message))
 		if (received_checksum == calculated_checksum): # Message is OK
			if (result_list[seqnum] == None):
				#print ("1-received message is OK. Placed message to " + str(seqnum))
				result_list[seqnum] = message[5:]
				packets_received_1 = packets_received_1 + 1
			# Else, received duplicate message, do nothing.
			#else:
				#print("1-Received duplicate message " + str(seqnum))


			# Find the ack number to send by finding the smallest index with an empty
			# slot in the receiving list.
			i = last_successful_ack+1
			while 1:
				if (result_list[i] == None):
					ack_message = packetize(i, '') # Make ack packet
					#print "1-Sending ack " + str(i)
					last_successful = i-1
					break
				i = i+1
			s1_socket.sendto(ack_message, (s1_name, s1_port)) # Send ack
		else: # Received corrupted message
			#print ("1-Received corrupted message")
			ack_message = packetize(last_successful_ack+1, '')
			s1_socket.sendto(ack_message, (s1_name, s1_port))


def receive_from_2(): # Thread 2 communicates through router 2
	global last_successful_ack
	global packets_received_2
	s2_socket = socket(AF_INET, SOCK_DGRAM)
	r2_socket = socket(AF_INET, SOCK_DGRAM)
	r2_socket.bind(('', r2_port))
	while 1:
		message = bytearray(message_size)
		r2_socket.recv_into(message)
		first_packet_arrived = True
		received_checksum = ord(chr(message[-1]))
		seqnum = int(message[:5]) # Sequence number of the message
		# Delete checksum field to calculate own checksum
		message = message[:len(message)-1]

		# Calculate own checksum
		calculated_checksum = ord(checksum(message))
 		if (received_checksum == calculated_checksum): # Message is OK
			if (result_list[seqnum] == None):
				#print "2-received message is OK. Placed message to " + str(seqnum))
				result_list[seqnum] = message[5:]
				packets_received_2 = packets_received_2 + 1
			# Else, received duplicate message, do nothing.

			# Find the ack number to send by finding the smallest index with an empty
			# slot in the receiving list.
			i = last_successful_ack+1
			while 1:
				if (result_list[i] == None):
					ack_message = packetize(i, '')
					#print ("2-Sending ack " + str(i))
					last_successful_ack = i-1
					break
				i = i+1
			s2_socket.sendto(ack_message, (s2_name, s2_port)) # Send ack
		else: # Received corrupted message
			#print ("2-Received corrupted message" + str(seqnum))
			ack_message = packetize(last_successful_ack+1, '')
			s2_socket.sendto(ack_message, (s2_name, s2_port))


def main():
	try:
		thread.start_new_thread(receive_from_1,())
		thread.start_new_thread(receive_from_2,())
		print "Ready to receive."
	except:
		print ("Error: unable to start thread")
		exit()

	# Wait for the first packet to arrive and start timer to calculate
	# file transfer time.
	while 1:
		sleep(0.01)
		if (packets_received_1 + packets_received_2 > 0):
			starting_time = datetime.now()
			print "Receiving packets..."
			break

	while 1:
		try:
			sleep(1)
			sys.stdout.write("\r" + str((packets_received_1 + packets_received_2)/100) + "% completed.")
			sys.stdout.flush()
			#sys.stdout.write(out)
			if (packets_received_1 + packets_received_2 >= 9999):
				ending_time = datetime.now()
				delta = ending_time - starting_time
				print("Process completed successfully.")
				print "Time elapsed: " + str(delta.seconds) + " seconds."
				# Log the output to the log file.
				with open ("results.log", "a+") as f:
					f.write(str(ending_time) + " - Time elapsed: " + str(delta.seconds) + "\n")
				break
		except(KeyboardInterrupt):
			print ("Process killed by user.")
			exit()

	# Create the output file.
	st = ''
	for e in result_list:
		if e == None:
			break
		st = st + str(e)
	with open('output.txt', 'w') as bit:
		bit.write(st)


if __name__ == '__main__':
	main()
