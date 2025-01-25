import sys
import socket
import threading
import json
from chatui import init_windows, read_command, print_message, end_windows

PORT = 80
NAME = ""
HOST = ""

def send_hello(s):

    global NAME    
    
    hello_packet = {
        "type": "hello",
        "nick": NAME.lower()
    }
    
    hello_json = json.dumps(hello_packet, indent=3).encode()
    
    s.send(hello_json)
    
    
def handle_input(s):

    global NAME
    
    while True:
        msg = read_command(f'{NAME.lower()} ')
    
        msg_packet = {
            "type": "chat",
            "message": msg
        }

        msg_json = json.dumps(msg_packet, indent=3).encode()

        s.send(msg_json)
        
        if (msg[0] == '/'):
            match msg[1]:
                case 'q':
                    # close connection
                    sys.exit(1)

def display_chat(data):
    name = data['nick']
    msg = data['message']

    print_message(f'{name}: {msg}')

def display_join(data):
    name = data['nick']

    print_message(f'*** {name} has joined the chat')

def display_leave(data):
    name = data['nick']

    print_message(f'*** {name} has left the chat')

def receive_packet(s):
    
    while True:
        
        d = s.recv(4096).decode()

        json_data = json.loads(d)

        match json_data['type']:

            case 'chat':
                display_chat(json_data)
            case 'join':
                display_join(json_data)
            case 'leave':
                display_leave(json_data)
    

def connect_server():

    global PORT
    global HOST
    global NAME

    s = socket.socket()

    s.connect((HOST, PORT))
    
    init_windows()

    send_hello(s)

    sending = threading.Thread(target=handle_input, args=[s])

    receiving = threading.Thread(target=receive_packet, args=[s])

    sending.start()
    receiving.start()


def main():

    global NAME
    global PORT
    global HOST

    try:
        NAME = sys.argv[1]
        HOST = sys.argv[2]
        PORT = int(sys.argv[3])
    except:
        print("Check Args!")
        sys.exit(1)
    
    connect_server()
    
    end_windows()

if __name__ == "__main__":
    main();
