import json
import socket
import subprocess
import time
import sys
import os
import signal
# server
def handle_client(client_socket,request):


    sniff_ble(client_socket,request)


    # client_socket.close()

def sniff_ble(client_socket,request):
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
    print(output)
    output = output.replace('\n', ',')
    print(output)
    client_socket.send(f"{output}\n".encode())
    print("send success....................")
    if error:
        client_socket.send(f"ERROR: {error}\n".encode())
    client_socket.close()

def ble_forge(client_socket,request):


    # command ="python"+request["scriptCommand"]
    command = "python advertiser.py"
    # args = request.split()[1]
    process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)

    output, error = process.communicate()

    print(output)
    client_socket.send(f"{output}\n".encode())
    if error:
        client_socket.send(f"ERROR: {error}\n".encode())
    client_socket.close()

def ble_relay(client_socket,request):
    command = "python " + +request["scriptCommand"] + " -s COM14 "
    # args = request.split()[1]
    process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
    if "sniff" in command:
        time.sleep(3)
        process.terminate()
    output, error = process.communicate()
    output = output.replace('\n', ',')
    print(output)
    print("test..........")
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
        if "sniff" in str(request):
            sniff_ble(client_socket, request)  # 处理客户端请求并关闭连接
        elif "adver" in str(request):
            print("adver........")
            ble_forge(client_socket, request)


        print("Connection closed")
        # client_socket.close()  # 关闭客户端连接套接字并释放资源
        # client_socket.close()
         # 在实际应用中，你可能希望循环而不是在这里使用break，以便处理多个客户端连接。这里只是为了简化示例。


if __name__ == "__main__":
          main()
