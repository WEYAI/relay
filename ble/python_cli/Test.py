import numpy as np
import uhd

# USRP B210配置
args = "type=b200"
usrp = uhd.usrp.MultiUSRP(args)

# 配置接收机参数
rate = 2e6  # 1 MHz采样率
freq = 2.43e9  # 2.4 GHz中心频率
gain = 20  # 收益设置
rx_streamer = usrp.get_rx_stream(uhd.stream_args(cpu_format="fc32", channels=[0]))

# 接收数据
num_samples = 10000  # 要接收的样本数
rx_buffer = np.zeros(num_samples, dtype=np.complex64)
rx_streamer.recv(rx_buffer)

# 保存数据到本地文件
file_path = "received_data.dat"
with open(file_path, "wb") as file:
    rx_buffer.tofile(file)

# 关闭接收机
usrp.close()
