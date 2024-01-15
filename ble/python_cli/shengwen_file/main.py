import socket
import subprocess
import os
import binascii
import select
import time
import re
import fcntl
import sys



class USRPServer:
    """
    init
    """
    def __init__(self, ip: str, port: int):
        """
        连接USRP服务器
        :param ip: 服务器ip地址
        :param port: 服务器端口号
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建 socket 对象，第一个参数为 socket.AF_INET，代表采用 IPv4 协议用于网络通信，第二个参数为 socket.SOCK_DGRAM，代表采用 UDP 协议用于无连接的网络通信
        self.s.bind((ip, port))
        
        print("USRP服务器启动完成...")
        
        


    def listen(self):
        usrp = USRP()
        self.state_machine = 'wait_connect'
        
        
        #Directive_definition
        
        #1.Connect state
        Client_Connect = binascii.unhexlify("7e010080")
        Server_Client_ConnectSuccess = binascii.unhexlify("7e01010080")
        Server_Client_ConnectFailed = binascii.unhexlify("7e01010180")
        
        #2.Open USRP state
        Open_USRP = binascii.unhexlify("7e020080")
        OpenUSRP_Success = binascii.unhexlify("7e02010080")
        OpenUSRP_Failed = binascii.unhexlify("7e02010180")
        OpenUSRP_DeviceEmpty = binascii.unhexlify("7e02010380")#设备为空状态码
        
        #3.Close USRP state
        Close_USRP = binascii.unhexlify("7e030080")
        CloseUSRP_Success = binascii.unhexlify("7e03010080")
        CloseUSRP_Failed = binascii.unhexlify("7e03010180")
        
        #4.Query USRP state
        Query_USRP = binascii.unhexlify("7e04010180")
        USRP_waitStart = binascii.unhexlify("7e0402010180")
        USRP_Working = binascii.unhexlify("7e0402010280")
        USRP_error = binascii.unhexlify("7e0402010380")
        
        
        Query_USRPServer = binascii.unhexlify("7e04010280")
        USRPServer_normal = binascii.unhexlify("7e0402020180")
        USRPServer_error = binascii.unhexlify("7e0402020280")
        
        
        Query_error = binascii.unhexlify("7e0402030380")
        Device_Success = binascii.unhexlify("111111111111")#设备成功打开返回该状态
        Device_Empty = binascii.unhexlify("000000000000")#设备为空时返回该状态
        
        # 开始监听进入与客户机交互数据阶段
        print("USRP服务器进入监听状态...\n")
        while True:
            data, addr = self.s.recvfrom(1024)  # 进入与客户端交互数据的循环阶段
            print("收到客户端 %s:%s" % addr + "发送过来的数据：%s" % data)  
            print("目前状态机为:%s" % self.state_machine)

            if self.state_machine == 'wait_connect':
                if data == Client_Connect:
                    print("客户端发送请求：Client_Connect")
                    self.s.sendto(Server_Client_ConnectSuccess, addr)
                    print("服务端反馈状态：Server_Client_ConnectSuccess")
                    self.set_statemachine('wait_openusrp')
                elif data == Query_USRPServer:
                    print("客户端发送请求：Query_USRPServer")
                    self.s.sendto(USRPServer_normal, addr)
                    print("服务端反馈状态：USRPServer_normal")
                    self.set_statemachine('wait_connect')
                else:
                    self.s.sendto(Server_Client_ConnectFailed, addr)
                    print("服务端反馈状态：Server_Client_ConnectFailed")
                    self.set_statemachine('wait_connect')




            elif self.state_machine == 'wait_openusrp':
                if data == Open_USRP:
                    print("客户端发送请求：Open_USRP")
                    open = usrp.open()
                    print("open:")
                    print(open)
                    if open == "Opening":
                        self.s.sendto(OpenUSRP_Success,addr)
                        print("服务端反馈状态：OpenUSRP_Success")                    
                        self.set_statemachine('usrp_opened')
                    else:
                        self.s.sendto(OpenUSRP_DeviceEmpty,addr)
                        print("服务端反馈状态：OpenUSRP_DeviceEmpty\n")                       
                elif data == Query_USRP:
                    print("客户端发送请求：Query_USRP")
                    self.s.sendto(USRP_waitStart, addr)
                    print("服务端反馈状态：USRP_waitStart")  
                elif data == Query_USRPServer:
                    print("客户端发送请求：Query_USRPServer")
                    self.s.sendto(USRPServer_normal, addr)
                    print("服务端反馈状态：USRPServer_normal") 
                    self.set_statemachine('wait_openusrp')
                elif data == Client_Connect:
                    print("客户端发送请求：Client_Connect")
                    self.s.sendto(Server_Client_ConnectSuccess, addr)
                    print("服务端反馈状态：Server_Client_ConnectSuccess\n")
                else:
                    self.s.sendto(OpenUSRP_Failed, addr)
                    print("服务端反馈状态：OpenUSRP_Failed") 
                    self.set_statemachine('wait_openusrp')


            elif self.state_machine == 'usrp_opened':
                if data == Close_USRP:
                    print("客户端发送请求：Close_USRP")
                    usrp.close()
                    self.s.sendto(CloseUSRP_Success, addr)  # 若 bytes 对象不为 b"exit"，则向地址为 addr 的客户端发送问候响应信息 b"Hello %s!\n"，其中 %s 是客户端发来的 bytes 对象。发送完毕后，继续等待任意 UDP 客户端发来数据
                    print("服务端反馈状态：CloseUSRP_Success") 
                    self.set_statemachine('wait_openusrp')

                elif data == Query_USRP:
                    print("客户端发送请求：Query_USRP")
                    if usrp.getstate() == None:
                        self.s.sendto(USRP_Working, addr)
                        print("服务端反馈状态：USRP_Working")
                    else:
                        self.s.sendto(USRP_waitStart, addr)
                        print("服务端反馈状态：USRP_waitStart")
                        self.set_statemachine('wait_openusrp')
                elif data == Query_USRPServer:
                    print("客户端发送请求：Query_USRPServer")
                    self.s.sendto(USRPServer_normal, addr)
                    print("服务端反馈状态：USRPServer_normal")
                    self.set_statemachine('usrp_opened')
                elif data == Client_Connect:
                    print("客户端发送请求：Client_Connect")
                    self.s.sendto(Server_Client_ConnectSuccess, addr)
                    print("服务端反馈状态：Server_Client_ConnectSuccess\n")
                elif data == Open_USRP:
                    print("客户端发送请求：Open_USRP")
                    self.s.sendto(OpenUSRP_Success,addr)
                    print("服务端反馈状态：OpenUSRP_Success")
                else:
                    self.s.sendto(CloseUSRP_Failed, addr)
                    print("服务端反馈状态：CloseUSRP_Failed")
                    self.set_statemachine('usrp_opened')

            else:
                self.s.sendto("00", addr)
                print('状态机错误!')

    def set_statemachine(self,s):
        print("执行完状态机为:%s\n" % s)
        self.state_machine = s



    def close(self):
        """
        关闭Linux终端
        :return:
        """
        self.ssh.close()


class USRP:
    
    """
    打开USRP
    """

    def open(self):
        """
        打开USRP
        :param ip:
        :param port:
        """
        #result = subprocess.run(f"/usr/bin/python3.6 -u /home/test/Desktop/GNU_Script/AM_sim_block.py", shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        #self.result = subprocess.Popen(["/usr/bin/python3.6", "-u", "/home/test/Desktop/GNU_Script/AM_sim_block.py"],stderr=subprocess.PIPE)
        self.result = subprocess.Popen(["/usr/bin/python3.6", "-u", "/mnt/hgfs/shengwen_file/AM_sim_block.py"], stderr=subprocess.PIPE)
        
        # 设置管道为非阻塞模式
        fcntl.fcntl(self.result.stderr, fcntl.F_SETFL, os.O_NONBLOCK)
        
        
        # 循环读取管道中的数据
        while True:
            #使用 select 函数检查管道是否有数据可读
            #print("stderr:")
            #print(self.result.stderr)
            read_ready, _, _ = select.select([self.result.stderr], [], [], 0)
            if read_ready:
                #如果有数据可读，立即读取数据并输出
                channel_data = self.result.stderr.read()
                sys.stderr.write(channel_data.decode('utf-8'))
                sys.stderr.flush()
                
                
                # 判断是否包含设备成功运行字符串，如果包含则停止循环
                if "Opening a USRP2" in channel_data.decode('utf-8'):
                    Open = "Opening"
                    return Open
                    break
                # 判断是否包含设备为空字符串，如果包含则停止循环
                if "Empty Device Address" in channel_data.decode('utf-8'):
                    Open = "Empty"
                    return Open
                    break

            #如果子进程已经结束并且管道中没有数据可读，终止循环
            if self.result.poll() is not None and not read_ready:
                break
        print('退出Open()函数')

        


    """
    关闭USRP
    """
    def close(self):
        """
        打开USRP
        :param ip:
        :param port:
        """
        # 读取pid
        #f1 = open(file='/home/test/Desktop/GNU_Script/count_pid.txt', mode='r')
        #pid = f1.read()
        #f1.close()
        return self.kill(self.result.pid)


    def kill(self, pid):
        # 本函数用于中止传入pid所对应的进程
        if os.name == 'nt':
            # Windows系统
            cmd = 'taskkill /pid ' + str(pid) + ' /f'
            try:
                os.system(cmd)
                return str(pid)+'killed'
            except Exception as e:
                return e
        elif os.name == 'posix':
            # Linux系统
            cmd = 'kill ' + str(pid)
            try:
                os.system(cmd)
                return str(pid) + 'killed'
            except Exception as e:
                return e
        else:
            return 'Undefined os.name'

    def getstate(self):
        print('returncode:',self.result.poll())
        return self.result.poll()



if __name__ == '__main__':
    server = USRPServer("192.168.10.1", 8083)
    server.listen()

