# coding:utf-8
import asyncio
import socket
import struct
import threading
import time

from Crypto.Cipher import AES
from bleak import BleakClient

wait = True
AES_KEY = b""
# 蓝牙设备的MAC地址
DEVICE_ADDRESS = "EA:8F:D9:27:CE:B3"
# DEVICE_ADDRESS = "B3:55:44:33:22:B3"
# DEVICE_ADDRESS = "a4:9f:89:af:b6:57"

DATA_SERVICE_UUID = "9aef0001-3d33-11e8-b467-0ed5f89f718b"
SEND_MESSAGE_UUID = "9aef0002-3d33-11e8-b467-0ed5f89f718b"
READ_MESSAGE_UUID = "9aef0003-3d33-11e8-b467-0ed5f89f718b"

BLE_CLIENT = None
tcp_socket = None
recv_data = b""


def thread_socket():
    global wait
    global tcp_socket
    global recv_data
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(('192.168.10.101', 33333))
    while True:
        temp_data = tcp_socket.recv(2)
        recv_data = temp_data + tcp_socket.recv(temp_data[1])
        if len(recv_data) > 2:
            if recv_data[2:7] == b"11111":
                recv_data = b""
                print("收到开始信号！")
                wait = False
            else:
                print('主开发板Socket接到的数据为：', recv_data.hex())
        time.sleep(0.2)


def aes_enc(key, data):
    print("SEND:", data.hex())
    cryptor = AES.new(key, AES.MODE_ECB)
    ciphertext = cryptor.encrypt(data)
    return ciphertext


def aes_dec(key, data):
    cryptor = AES.new(key, AES.MODE_ECB)
    plain_text = cryptor.decrypt(data)
    print("RECV:", plain_text.hex())
    return plain_text


def gen_ts_packet():
    print("gen_ts_packet")
    timestamp = int(time.time())
    temp = b"\x08\x01\x04" + struct.pack(">I", timestamp)
    check_sum = 0
    for a in temp:
        check_sum += a
    return temp + struct.pack(">B", check_sum & 0xFF) + b"\x00" * 8


async def main(address):
    global BLE_CLIENT
    async with BleakClient(address) as client:
        try:
            # 是否连接
            if not client.is_connected:
                print('开始连接设备...')
                client.connect()
            print(f"连接: {client.is_connected}")
            # 是否配对
            paired = await client.pair(protection_level=2)
            print(f"配对: {paired}")
            # 开启通知的接收
            await client.start_notify(READ_MESSAGE_UUID, notify_callback)
            # if client.is_connected and paired:
            if client.is_connected:
                print("连接完成")
                BLE_CLIENT = client
                # await client.write_gatt_char(SEND_MESSAGE_UUID, openDoor_send)
            await asyncio.sleep(100.0)
            print('Disconnected')
        except Exception as e:
            print(f"Exception during write_and_listen loop: {e}")
        finally:
            # 结束监听
            try:
                await client.stop_notify(READ_MESSAGE_UUID)
                # 断开与蓝牙设备的连接
                await client.disconnect()
                print("结束")
            except:
                pass


# 回调监听
async def notify_callback(sender, data):
    global AES_KEY
    global tcp_socket
    global BLE_CLIENT
    global recv_data
    try:
        # 处理从设备发来的Notify数据
        print(f"Received : {data.hex()}")
        print("-" * 60)
        if len(data) >= 16:
            l1 = len(data) + 4 + 3
            l2 = len(data) + 3
            header = struct.pack("<BBHHBH", 2, l1, l2, 4, 0x1b, 0xf)
            print("主发送给从：", (header + data).hex())
            tcp_socket.send(header + data)
            while True:
                if len(recv_data) > 0:
                    temp_data = recv_data
                    recv_data = b""
                    print("发送给设备:", temp_data[-16:].hex())
                    await BLE_CLIENT.write_gatt_char(SEND_MESSAGE_UUID, temp_data[-16:])
                    break
                time.sleep(0.05)
    except Exception as e:
        print(f"notify_callback: {e}")


if __name__ == '__main__':
    # aes_key = binascii.a2b_hex("8ca900e5777efecf237015eb00263b03")
    # aes_enc(aes_key, binascii.a2b_hex("04013035000000000000000000000000"))
    # aes_dec(aes_key, binascii.a2b_hex("b139c05949da117a67d06337f554966f"))
    th_server = threading.Thread(target=thread_socket, args=())
    th_server.start()

    print("等待手机连接从开发板")
    while wait:
        time.sleep(0.01)
    print("主开发板开始连接锁")
    time.sleep(1)
    asyncio.run(main(DEVICE_ADDRESS))
