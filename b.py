from socket import *
from datetime import datetime
from time import sleep
import thread

# Address definitions
s_address = '10.10.1.1'
d1_address = '10.10.3.2'
d2_address = '10.10.5.2'

# Port definitions
send_to_d1_port = 4007
send_to_d2_port = 4008
recv_from_s_port = 4009
recv_from_d_port = 4000

# TCP related variables
receiving_message_size = 500 # Incoming message size from source
data_string = '' # Variable to keep incoming data from source
start = False # When start is set to True, broker starts to send messages to destination.
			  # start is set to True when 10 packets arrive from the source. This is
			  # required since transmission to destination will be done in window of packets.

# RDT related variables
payload_size = 500 # Sent message size = payload_size + 6
				   # 6 additional bytes are needed. 5 is for sequence number, 1 for checksum.
ack = 0 # Last ACK received
prev_ack = -1 # Ack received before the current ack
duplicate_ack_count = 0 # Kept to detect if duplicate acks reaches 3.
ack_size = 6 # 5 bytes: expected seqnum, 1 byte: checksum
timeout = 1 # Timeout duration in seconds.
timer_start = None # The time when a window is sent.
switch = False # Variable used to switch between routes.
send_to_d1_socket = None # Socket for communicating with destination
send_to_d2_socket = None # Socket for communicating with destination

# Window related variables
next_seqnum = 0
base = -1
default_wnd_size = 2 # Window size resets to this value (like TCP Tahoe)
window_size = 2 # Current window size

'''
# RDT packet format
sequence number (5 bytes)
data (receiving_message_size bytes)
checksum (1 byte)
'''


def receive_from_s():
	'''
	Thread function to receive data from source through a TCP connection.
	'''
	global data_string
	global start

	# Start listening
	recv_from_s_socket = socket(AF_INET, SOCK_STREAM)
	recv_from_s_socket.bind(('', recv_from_s_port))
	recv_from_s_socket.listen(1)

	connection_socket, addr = recv_from_s_socket.accept() # Client(source) is waited to connect

	i = 0 # variable kept for counting packets, after value 10, it will signal other threads
	while 1:
		data_string = data_string + connection_socket.recv(payload_size)
		# Upon receiving 10 TCP segments of data, start sending them
		# to destination.
		if (i == 10):
			start = True # Signal other threads to start
		i = i+1
		# Check if the file is completely received.
		if (len(data_string) == 5000000):
			break
	print "Completed receiving from source."
	#Close sockets for succesful ending
	connection_socket.close()
	recv_from_s_socket.close()


def checksum(msg):
	'''
	Function calculates the checksum of the given message.
	Returns a byte.
	Works like a hash function with mod 256 operation.
	Mod operand should be 256 so that it will produce a one-byte result.
	'''
	chksum = 0
	# add bytes
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
	while len(seqnum) < 5: # Fill with leading zeros.
		seqnum = '0' + seqnum
	packet = seqnum + data # Combine
	packet = packet + checksum(packet) # Add checksum
	return packet


def send_window(ack):
	'''
	Function sends window_size amount of packets. Given ack number is the
	sequence number of the first packet to send.
	'''
	global window_size
	global timer_start
	global base
	global next_seqnum
	global file_size
	global switch
	global start
	global data_string

	# we take ack value before other operations, since we don't want it to change 
	# during the calculations due to use of threads

	i = ack # Iterator for packets in the window.
	base = ack # Set the base of the window
	try:
		while i < ack+window_size: # we did use ack variable instead of i, possible making large window size, 
								   # which is in favour of us in threading issue
			#print "sending packet " + str(i)
			data = data_string[i*payload_size:(i+1)*payload_size]
			packet = packetize(i, data) # creates packet with checksum and sequence number

			# Broker should distribute the packets to both routes equally.
			# The route is decided based on the value of the switch variable.
			if (switch):
				sckt = send_to_d1_socket
				addr = (d1_address, send_to_d1_port)
			else:
				sckt = send_to_d2_socket
				addr = (d2_address, send_to_d2_port)
			switch = not switch # flipped in every iteration to change path

			sckt.sendto(packet, addr)
			i = i + 1
		next_seqnum = i

	# When window includes out-of-list elements, transmission is completed.
	except(IndexError):
		if (not start):
			print "Exiting send thread."
			exit()

def update_window(wnd_size_increment, ack):
	'''
	Function assumes a window was previously sent and updates the window
	depending on the value of the new ack. Sends the new data included
	in the window. Optionally it can increase the window size
	'''
	global window_size
	global base
	global next_seqnum
	global switch
	global start

	new_packet_amount = ack - base + wnd_size_increment
	#print "sending " + str(new_packet_amount) + " more packets"

	try:
		# Send new packets starting from base+window_size
		for i in range (new_packet_amount):
			#print "sending new packet " + str(next_seqnum)
			data = data_string[next_seqnum*payload_size:(next_seqnum+1)*payload_size]
			packet = packetize(next_seqnum, data) # creates packet with checksum and sequence number

			# Broker should distribute the packets to both routes equally.
			if (switch):
				sckt = send_to_d1_socket
				addr = (d1_address, send_to_d1_port)
			else:
				sckt = send_to_d2_socket
				addr = (d2_address, send_to_d2_port)
			switch = not switch # flipped in every iteration to change path

			sckt.sendto(packet, addr)
			next_seqnum = next_seqnum + 1
		base = ack # update base
		window_size = window_size + wnd_size_increment # update window size, which is exponential increase

	# When window includes out-of-list elements, transmission is completed.
	except(IndexError):
		if (not start):
			print "Exiting send thread."
			exit()


def send():
	'''
	Thread function to send data to destination.
	'''
	global ack
	global window_size
	global base
	global duplicate_ack_count
	global default_wnd_size
	global send_to_d1_socket
	global send_to_d2_socket
	global timer_start

	send_to_d1_socket = socket(AF_INET, SOCK_DGRAM)
	send_to_d2_socket = socket(AF_INET, SOCK_DGRAM)

	last_known_ack = ack # Used to check if a new ack arrived.

	# Send initial packets
	send_window(ack)
	timer_start = datetime.now() # Later timeout will be checked.

	while 1:
		# Ack should be copied to a local variable, otherwise its value can be
		# changed by the other thread.
		local_ack = ack

		# If all packets are transmitted, end thread.
		if (ack == 10000):
			exit()

		# Check timeout
		delta = datetime.now()-timer_start
		if (delta.seconds >= timeout): # Timeout occurred. Resend packet.
			#print "Timeout."
			window_size = default_wnd_size # reset window size
			timer_start = datetime.now() # reset timeout, later timeout will be checked.
			send_window(local_ack) # call related function to start sending from packet that timeout event occur
			continue

		if (local_ack >= last_known_ack): # Check if a new ack was received.
			last_known_ack = local_ack # Update last known ack
			if (duplicate_ack_count >= 3): # Lost a packet, retransmit.
				#print "Packet " + str(local_ack) + " was lost."
				duplicate_ack_count = 0 # Reset counter
				window_size = default_wnd_size # Reset window size
				send_window(local_ack)# call related function to start sending from packet that duplicate_ack event occur
				continue
			elif (local_ack > base): # A valid ack
				# Successful transmission, update window & increase window size
				timer_start = datetime.now() # Update timer, later timeout will be checked.
				update_window(1, local_ack) # call related function to start sending regularly
				continue
		# Else: no new ack, continue


def receive():
	'''
	Thread function to receive ACK's from destination
	'''
	global ack
	global duplicate_ack_count
	global prev_ack
	global start

	receive_socket = socket(AF_INET, SOCK_DGRAM)
	receive_socket.bind(('', recv_from_d_port))

	while 1:
		message = bytearray(ack_size)
		receive_socket.recv_into(message)
		received_checksum = ord(chr(message[-1])) # Obtain the checksum

		# Calculate checksum
		message = message[:len(message)-1] # Not include checksum field
		calculated_checksum = ord(checksum(message))

		if (received_checksum == calculated_checksum): # Received ack is OK, not corrupt
			ack = int(message[:5])

			# Process ends when ack for 10000th packet is received.
			if (ack >= 10000):
				print "Exiting receive thread"
				start = False # Signal 'send thread' to stop.
				exit()
			if (ack == prev_ack): # Check if received ack is a duplicate.
				duplicate_ack_count = duplicate_ack_count + 1
			else:
				prev_ack = ack
				duplicate_ack_count = 0 # if not duplicate, then reset the variable
			#print "Ack OK: " + str(ack)
		# Else, ack is corrupted, do nothing.


def main():
	try:
		thread.start_new_thread(receive_from_s, ())
		print "Broker is running."
	except:
		print "Error: unable to start thread"
		exit()

	# Wait until 10 segments arrive from source. When start variable
	# becomes True, transmission to destination can start.
	while 1:
		sleep(2)
		if (start):
			try:
				thread.start_new_thread(send, ())
				thread.start_new_thread(receive, ())
				print "Started sending to destination."
				break
			except:
				print "Error starting RDT threads."

	# Wait until transmission to destination ends. The variable start is set
	# to False when transmission is completed.
	while 1: # we did this to close peacefully
		try:
			sleep(5)
			if (not start):
				print "Process completed."
				sleep(1)
				exit()
		except(KeyboardInterrupt):
			print "Process stopped by user."
			exit()


if __name__ == '__main__':
	main()
