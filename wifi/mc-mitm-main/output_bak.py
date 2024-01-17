import sys
import re



data = []
# 匹配Wi-Fi MAC地址的正则表达式
mac_address_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
# 测试例子
test_cases = [
    "00:1A:2B:3C:4D:5E",
    "01-23-45-67-89-AB",
    "a1:b2:c3:d4:e5:f6",
    "invalid_mac_address",
]
test1 = "00:1A:2B:3C:4D:5E -35       7      0      0    9     54     WPA2  CCMP    PSK  xiao"


# for i in range(1000):
#     c = sys.stdin.readline()
#     len_c = len(c)
#     print("len——c........................")
#     print(len_c)
#     if len_c > 3:
#         line = c.split()
#         len_line = len(line)
#         if len_line > 4:
#             print("split................")
#             print(line)
#             mac = line[0]
#             print("mac...................")
#             print(mac)
#             ssid = line[len_c - 1]
#             print("ssid.................")
#             print(ssid)
#             if line:
#                 if mac_address_pattern.match(mac):
#                     data.append("["+line+"]")
#                     data.append("["+ssid+"]")
            


# print(data)
            
if __name__ == "__main__":
        test3 = "                                              "
        test0 = "CH  10 ] [ Elapsed: 6 s ] [  2024-01-16  08:01"
        test1 = "00:1A:2B:3C:4D:5E -35       7      0      0    9     54     WPA2  CCMP    PSK  xiao"
        line = test1.split()
        len_line = len(line)
        print(len_line)
        if len_line > 4:
            print("split................")
            print(line)
            mac = line[0]
            print("mac...................")
            print(mac)
            ssid = line[-1]
            print("ssid.................")
            print(ssid)
            if line:
                if mac_address_pattern.match(mac):
                    data.append("["+mac+"]")
                    data.append("["+ssid+"]")










