import subprocess

# 要执行的长命令
long_command = "/usr/bin/python3.6 -u /mnt/hgfs/shengwen_file/AM_sim_block.py"

# 使用subprocess.run()函数执行长命令并获取执行结果
result = subprocess.run(long_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 获取命令执行结果
stdout = result.stdout.decode().strip()  # 标准输出
stderr = result.stderr.decode().strip()  # 错误输出
returncode = result.returncode  # 命令返回值


def open():
        """
        打开USRP
        :param ip:
        :param port:
        """
        #result = subprocess.run(f"/usr/bin/python3.6 -u /home/test/Desktop/GNU_Script/AM_sim_block.py", shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        #self.result = subprocess.Popen(["/usr/bin/python3.6", "-u", "/home/test/Desktop/GNU_Script/AM_sim_block.py"],stderr=subprocess.PIPE)
        #self.result = subprocess.Popen(["/usr/bin/python3.6", "-u", "/mnt/hgfs/shengwen_file/AM_sim_block.py"],stderr=subprocess.PIPE)
        #return self.result
        
        long_command = "/usr/bin/python3.6 -u /mnt/hgfs/shengwen_file/AM_sim_block.py"# 要执行的长命令
        result = subprocess.run(long_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        returncode = result.returncode  # 命令返回值
        stdout = result.stdout.decode().strip()  # 标准输出
        stderr = result.stderr.decode().strip()  # 错误输出
        
        # 打印命令执行结果
        if returncode == 0:
            print("命令执行成功")
            #print("标准输出：", stdout)
            return stdout
        else:
            print("命令执行失败")
            #print("错误输出：", stderr)
            return stderr


print(open())