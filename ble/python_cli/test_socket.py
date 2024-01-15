import json
import socket
import subprocess
import time
import sys
import os
import signal
# server
def handle_client(client_socket,request):
    command = "python -u " + request["scriptCommand"]
    if "sniff" in command:
        command = "python -u " + request["scriptCommand"] + " -s COM18"
    elif "" in command: 
        pass
    print(command)
    # args = request.split()[1]
    process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
    print("process run")
    if "sniff" in command:
        time.sleep(3)
        process.terminate()
    output, error = process.communicate()
    print("进程输出。。。。。")
    print(output)
    print("send success....................")
    client_socket.send(f"{output}\n".encode())
    if error:
        client_socket.send(f"ERROR: {error}\n".encode())
    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", 8888))  # 绑定到特定端口，例如8000

    server.listen(5)  # 最大连接数为5

    hostname = socket.gethostname() 
    print(hostname)

    host = socket.gethostbyname(hostname) # 获取自己的主机ip
    print(host)

    print("Server started")
    while True:
        client_socket, address = server.accept()  # 接受客户端连接请求
        print(f"Accepted connection from {address}")
        request = client_socket.recv(1024).decode()
        request = json.loads(request)
        print(request)
        handle_client(client_socket, request)  # 处理客户端请求并关闭连接
        print("Connection closed, waiting for client.........")


if __name__ == "__main__":
          main()
