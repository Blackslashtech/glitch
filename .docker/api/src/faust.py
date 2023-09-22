
import pymongo
import socket
import sys
import threading


client = pymongo.MongoClient('mongodb://db:27017/')
db = client['range']

# Function to process a submitted flag
def process_flag(flag):
    if db.flags.find_one({'flag': flag}):
        return "OK"
    else:
        return "ERR"


def faust_submitter():
    # Create flag submission listener
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', 666)
    sock.bind(server_address)
    sock.listen(1)
    while True:
        connection, client_address = sock.accept()
        try:
            connection.sendall(b'Demo FAUST CTF 2023 Flag Submission Server\nOne flag per line please!\n\n')
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                flags = data.decode().strip().split('\n')
                for flag in flags:
                    response = process_flag(flag)
                    response_message = f'{flag} {response}\n'
                    connection.sendall(response_message.encode())
                
        finally:
            connection.close()


def run():
    # Start the flag submission server
    faust_thread = threading.Thread(target=faust_submitter, daemon=True)
    faust_thread.start()