import sys
import socket
import select
import json
from chatui import init_windows, read_command, print_message, end_windows

PORT = 80

# idk maybe they sould be local but it both work fine
user_dict = {}
listen_sockets = set()


def is_hello(data):
    
    if (data["type"] == "hello" and len(data) != 0):
        return 1
    else:
        return 0

def is_chat(data):
    return data["type"] == "chat"

def join_chat(name, s):

    join_packet = {
        "type": "join",
        "nick" : name.lower()
    }

    json_join = json.dumps(join_packet, indent=3).encode()

    for sock in listen_sockets:
        if sock != s:
            sock.sendall(json_join)

def leave(s, sock, name):
    del user_dict[sock]
    listen_sockets.remove(sock)
    sock.close()
    leave_chat(name, s)

def special_input(msg, s, sock, name):
    if(msg[0] == '/'):
        match msg[1]:
            case 'q':
                #close connection on that socket
                leave(s, sock, name)
                return 1
            case _:
                return 0
    else:
        return 0 

def leave_chat(name, s):

    leave_packet = {
        "type": "leave",
        "nick": name.lower()
    }
    
    json_leave = json.dumps(leave_packet, indent=3).encode()

    for sock in listen_sockets:
        if sock != s:
            sock.sendall(json_leave)
    

def broadcast_msg(msg, name, s):
    
    msg_packet = {
        "type" : "chat",
        "nick": name.lower(),
        "message": msg
    }

    json_msg = json.dumps(msg_packet, indent=4).encode()
    
    for sock in listen_sockets:
        if sock != s:
            sock.sendall(json_msg)
        
def run_server():

    global PORT

    s = socket.socket()

    s.bind(("", PORT))
    
    s.listen()

    listen_sockets.add(s)

    while True:
    
        # Multi threading!

        ready_reads, _, _ = select.select(listen_sockets, {}, {})

        for sock in ready_reads:

            if (sock == s):
                new_conn = s.accept()
                new_socket = new_conn[0]

                listen_sockets.add(new_socket)
                
            else:
                 
                data = sock.recv(4096).decode()
                
                json_data = json.loads(data)

                if not data:
                    #delete from user_dict and use leave_chat function
                    name = user_dict[sock]
                    leave(s, sock, name)

                if is_hello(json_data):
                    name = json_data['nick']
                    user_dict[sock] = name
                    join_chat(name, s)
     
                if is_chat(json_data):
                    msg  = json_data['message']
                    name = user_dict[sock] # check if none
                    
                    if (not special_input(msg, s, sock, name)):
                        broadcast_msg(msg, name, s)

                    

def main():

    global PORT

    try:
	    PORT = int(sys.argv[1])
    except Exception as e:
	    print(f"ERROR: USAGE {sys.argv[0]} <PORT>")
	    sys.exit(1)

    run_server()




if __name__ == "__main__":
	main();
