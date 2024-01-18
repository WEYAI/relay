import sys
import re



data = []
# 匹配Wi-Fi MAC地址的正则表达式
mac_address_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
# 测试例子

for i in range(1000):
    c = sys.stdin.readline()
    
    len_c = len(c)
    if len_c > 3:
        line = c.split()
        len_line = len(line)
        if len_line > 4:
            mac = line[0]
            ssid = line[-1]
            if line:
                if mac_address_pattern.match(mac):
                    ssid = ssid
                    new_ssid = ssid.replace("\x1b[0k", "")
                    data.append("["+mac+","+new_ssid+"]")
                    
                
            

data_set = set(data)
print(data_set)
            










