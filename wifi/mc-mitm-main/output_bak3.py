import sys
import re



data = []
# 匹配Wi-Fi MAC地址的正则表达式
mac_address_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
# 测试例子

for i in range(1000):
    c = sys.stdin.readline()
    print(c)
    len_c = len(c)
    print("len——c........................")
    print(len_c)
    if len_c > 3:
          data.append(c+"\n")  
print(data)
            










