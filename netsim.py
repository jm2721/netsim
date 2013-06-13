# Network simulator
import string, sys
import random

# Error Codes:
# 0 - successful delivery
# 1 - No outgoing links.
# 2 - Exceeded time to live restraint (512 hops)

class Host():
	def __init__(self, name):
		self.name = name
		self.links_to = []
	def add_link_to(self, link_host):
		self.links_to.append(link_host)

class Message():
	def __init__(self, sending_host, receiving_host):
		self.sending_host = sending_host
		self.receiving_host = receiving_host
		self.sending_host_name = sending_host.name
		self.hops = 1
		self.last_error = 0
	
	def route(self):
		if not self.sending_host.links_to:
			self.hops = 0
			self.last_error = 1
		else:	
			self.rand = random.randint(1,100)
			self.take_route = self.rand % len(self.sending_host.links_to)
			self.temp = self.sending_host.name
			self.sending_host = self.sending_host.links_to[self.take_route]
			print "     Picking link from " + self.temp + " to " + self.sending_host.name
			if self.sending_host == self.receiving_host:
				# Return 0 for success
				self.last_error = 0
			else:
				self.hops += 1	
				if self.hops > 512:
					self.hops = 0
					self.last_error = 2
				else: 
					self.route()
					return self.last_error
# Just find the specified string in the list
# Python probably has a built in method for this... but it's simple enough
def find_word(lines, string):
	temp = 0
	for element in lines:
		if element == string:
			return temp
		temp = temp + 1
def parse(item):
	_from = item[0:string.find(item, "TO")].strip()
	_to = item[string.find(item, "TO")+2:].strip()
	return [_from, _to]

# Checks if the host was defined prior to it being
# used in a link or message
def check_defined(link_or_msg, hosts):
	for element in link_or_msg:
		if parse(element)[0] not in hosts:
			print "Host " + parse(element)[0] + " was not defined under HOSTS"
			print "Program exiting..."
			sys.exit()
		if parse(element)[-1] not in hosts:
			print "Host " + parse(element)[-1] + " was not defined under HOSTS"
			print "Program exiting..."
			sys.exit()

def return_object_from_name(name, host_objects_list):
	for element in host_objects_list:
		if element.name == name:
			return element
	# Print an error if it wasn't found
	print "Error"
	sys.exit()

def initialize_host_objects(hosts, links, messages):
	host_objects = []

	for element in hosts:
		host_objects.append(Host(element))
	
	for element in host_objects:
		for link in links:
			if parse(link)[0] == element.name:
				element.add_link_to(return_object_from_name(parse(link)[-1], host_objects))
	
	return host_objects

def initialize_msg_objects(messages, host_objs):
	msg_objs = []
	for msg in messages:
		msg_objs.append(Message(return_object_from_name(parse(msg)[0], host_objs), return_object_from_name(parse(msg)[1], host_objs)))
	
	return msg_objs

def read_from_file(filename):
	random.seed()
	
	try:
		file_stream = open(filename, 'r')
	except IOError:
		print "File name does not exist. Exiting program..."
		sys.exit()
	 
	
	lines = []	
	for line in file_stream:
		clean_line = line.strip()
		lines.append(clean_line)
	network_name = lines[1]

	hosts = lines[3:find_word(lines, "LINKS")]
	links = lines[find_word(lines, "LINKS")+1:find_word(lines, "MESSAGES")]	
	messages = lines[find_word(lines, "MESSAGES")+1:find_word(lines, "END")]

	check_defined(links, hosts)
	check_defined(messages, hosts)

	file_stream.close()
	return [hosts, links, messages, network_name]

def simulate(msg_objs, network_name):
	print "Simulating network: " + network_name
	
	average = 0.0
	delivered = 0.0
	for obj in msg_objs:
		print " Sending message from " + obj.sending_host_name + " to " + obj.receiving_host.name
		obj.route()
		if obj.last_error == 0:
			print " Routing was successful between " + obj.sending_host_name + " and " + obj.receiving_host.name
			print " Message delivered in " + str(obj.hops) + " hops"
			delivered += 1
			average += obj.hops
		elif obj.last_error == 1:
			print " Routing unsuccessful. Host " + obj.sending_host.name + " has no outgoing links"
		elif obj.last_error == 2:
			print " Routing unsuccessful. Exceeded time to live constraint."
	print "Simulation ending"
	print ""
	print "Delivered " + str(delivered) + " out of " + str(len(msg_objs)) + " messages, success rate " + str(100*delivered/len(msg_objs)) + "%"
	print "Delivery required an average of " + str(average) + " hops"
	average = average/len(msg_objs)

# If this is not an imported module, run the simulation on some file
if __name__ == '__main__':
	_file = raw_input("Please input the name of the file with the network: ")
	
	read_data = read_from_file(_file)
	hosts = read_data[0]
	links = read_data[1]
	messages = read_data[2]
	network_name = read_data[3]

	host_objs = initialize_host_objects(hosts, links, messages)
	msg_objs = initialize_msg_objects(messages, host_objs)

	simulate(msg_objs, network_name)
