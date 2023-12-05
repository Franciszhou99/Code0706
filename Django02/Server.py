import socket
import sys

# 创建 socket 对象
serversocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)

# 获取本地主机名
host = socket.gethostname()

port = 9999

# 绑定端口号
serversocket.bind((host, port))

# 设置最大连接数，超过后排队
serversocket.listen(2)

while True:
    # 建立客户端连接
    socket1, addr = serversocket.accept()

    print("连接地址: %s-- %s " % (str(addr), str(socket1)))

    msg = '欢迎访问菜鸟教程！' + "\r\n"
    socket1.send(msg.encode('utf-8'))
    #socket1.close()