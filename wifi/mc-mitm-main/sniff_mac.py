import subprocess
import time

# 定义要运行的一系列命令
commands = [
    "airmon-ng start wlan1",
    "airodump-ng wlan1mon | output.py",
    # 添加更多的命令...
]

# 使用循环遍历并运行每个命令
for command in commands:
    print(f"Running command: {command}")
    try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
            if "airodump" in command:
                time.sleep(5)
                process.terminate()
            output, error = process.communicate() 
            print("进程输出。。。。。")
            print(output)
            print(error)
            if error:
                    pass
    except subprocess.CalledProcessError as e:
        print(f"Error while running the command: {e}")
        print("Command output:", e.output)
    print("=" * 50)  # 打印分隔线



