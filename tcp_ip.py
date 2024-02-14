import time
import socket
from file_reader import FileReader

class TCPClient:
    def __init__(self, server_ip, server_port):
        file_reader = FileReader()
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.request_delay = file_reader.load_json("../settings/dsp.json")["time between frames"]

    def make_multiple_requests(self, msg, frame_count):
        frames = []
        for f in range(frame_count):
            self.send_message(msg)
            frames.append(self.receive_response())
            time.sleep(self.request_delay)
        return frames

    def connect(self):
        self.client_socket.connect((self.server_ip, self.server_port))

    def send_message(self, message):
        self.client_socket.sendall(bytes(message))

    def receive_response(self, buffer_size=2000):
        return self.client_socket.recv(buffer_size).decode("UTF-8").split(" ")

    def close_connection(self):
        self.client_socket.close()
