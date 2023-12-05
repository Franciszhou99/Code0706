import socket
import threading

# 客户端地址 名称
addr_name = {}

# 所有客户端
all_clients = []

# 名称 客户端
name_client = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()

port = 9999

server.bind((host, port))

server.listen(5)

lock = threading.Lock()

print("开启聊天室")


def handle_sock(sock, addr):
    while True:
        try:
            data = sock.recv(1024)
            msg = data.decode("utf-8")
            print("send msg")
            from_name = addr_name[str(addr)]
            if msg.startswith('@'):
                index = msg.index(' ')
                # 私聊人
                to_name = msg[1:index]
                # 接收者客户端
                to_sock = name_client[to_name]
                # 发送的消息
                to_msg = msg[index:]
                send_one(to_sock, addr, from_name + ":" + to_msg)
            else:
                # 群发消息
                send_all(all_clients, addr, from_name + ":" + msg)
        except ConnectionResetError:
            exit_name = addr_name[str(addr)]
            exit_client = name_client[exit_name]
            all_clients.remove(exit_client)
            msg = exit_name + " 退出了群聊"
            send_all(all_clients, addr, msg)
            break


def send_all(socks, addr, msg):
    for sock in socks:
        sock.send(msg.encode("utf-8"))


def send_one(sock, addr, msg):
    sock.send(msg.encode("utf-8"))


while True:
    sock, addr = server.accept()
    name = sock.recv(1024).decode("utf-8")
    addr_name[str(addr)] = name
    name_client[name] = sock
    all_clients.append(sock)
    hello = name + "加入了聊天室"
    send_all(all_clients, addr, hello)
    client_thread = threading.Thread(target=handle_sock, args=(sock, addr))
    client_thread.start()