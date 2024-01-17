import json
import socket
import subprocess
import time
import sys
import os
import signal
# server
def handle_client(client_socket,request):
    command = "sudo python3 -u " + request["scriptCommand"]
    if "sniff_receiver" in command:
        command = "sudo python3 -u " + request["scriptCommand"] + " -s COM18"
    if "mc-mitm" in command:
        command = request["scriptCommand"] 
    print(command)
    # args = request.split()[1]
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
    print("process run")
    if "sniff_receiver" in command:
        time.sleep(3)
        process.terminate()
    elif "mc-mitm" in command:
        time.sleep(5)
        process.terminate()
    output, error = process.communicate()
    print("进程输出。。。。。")
    print(output)
    print("send success....................")
    client_socket.send(f"{output}\n".encode())
    if error:
        client_socket.send(f"ERROR: {error}\n".encode())
    # client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", 8888))  # 绑定到特定端口，例如8000
    server.listen(5)  # 最大连接数为5
    print("Server started")
    while True:
        client_socket, address = server.accept()  # 接受客户端连接请求
        print(f"Accepted connection from {address}")
        request = client_socket.recv(1024).decode()
        request = json.loads(request)
        print(request)
        handle_client(client_socket, request)  # 处理客户端请求并关闭连接
        print("Connection closed, waiting for client.........")
        client_socket.close()


if __name__ == "__main__":
          main()
