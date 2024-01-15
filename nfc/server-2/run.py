import sys
import tkinter as tk
import subprocess
import server

HOST = "0.0.0.0"
PORT = 5566

# 创建主窗口
window = tk.Tk()
window.title("Python脚本执行客户端")

# 创建多行文本框
output_text = tk.Text(window)
output_text.pack()


# 创建一个函数来执行Python脚本并将输出显示在文本框中
def run_python_script():
    # 清空文本框
    output_text.delete("1.0", tk.END)

    # 执行Python脚本
    script_path = "server.py"  # 你的Python脚本的路径
    try:
        result = subprocess.run(["python", script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output_text.insert(tk.END, result.stdout)
    except Exception as e:
        output_text.insert(tk.END, f"Error: {e}")


# 创建一个按钮来触发脚本执行
run_button = tk.Button(window, text="运行Python脚本", command=run_python_script)
run_button.pack()

# 启动主循环
window.mainloop()


output = tk.StringVar()
sys.stdout = output

server.NFCGateServer((HOST, PORT), server.NFCGateClientHandler).serve_forever()

output_text.insert(tk.END, output.get())
