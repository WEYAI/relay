#!/usr/bin/env python3

# Written by Sultan Qasim Khan
# Copyright (c) 2020, NCC Group plc
# Released as open source under GPLv3

import argparse, sys, binascii, socket, time, struct, threading
from sniffle_hw import SniffleHW, BLE_ADV_AA, PacketMessage, DebugMessage, StateMessage, MeasurementMessage
from packet_decoder import DPacketMessage, ConnectIndMessage

# global variable to access hardware
hw = None

client_socket = None


def socket_server():
    global hw
    global client_socket
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp_server_socket.bind(('127.0.0.1', 9999))
    tcp_server_socket.bind(('127.0.0.1', 33333))
    tcp_server_socket.listen(30)
    print("开启socket")
    client_socket, clientAddr = tcp_server_socket.accept()
    print("连接地址: %s" % str(clientAddr))
    while True:
        recv_data = client_socket.recv(1024)
        if len(recv_data) > 2:
            print('Socket接到的数据为：', recv_data.hex())
            pdutype = recv_data[0] & 3
            if recv_data[2] == 0x2C:
                hw.cmd_transmit(pdutype, binascii.a2b_hex("1700040009150c000c0d008b719ff8d50e67b4e811333d0200ef9a"))
            else:
                hw.cmd_transmit(pdutype, recv_data[2:])
        time.sleep(0.2)


def main():
    print('开始运行')
    aparse = argparse.ArgumentParser(description="Connection initiator test script for Sniffle BLE5 sniffer")
    aparse.add_argument("-s", "--serport", default=None, help="Sniffer serial port name")
    aparse.add_argument("-m", "--mac", default=None, help="macAddr")
    args = aparse.parse_args()

    th_server = threading.Thread(target=socket_server, args=())
    th_server.start()
    global hw
    hw = SniffleHW(args.serport)

    # set the advertising channel (and return to ad-sniffing mode)
    hw.cmd_chan_aa_phy(37, BLE_ADV_AA, 0)

    # pause after sniffing
    hw.cmd_pause_done(True)

    # Accept/follow connections
    hw.cmd_follow(True)

    # turn off RSSI filter
    hw.cmd_rssi()

    # Turn off MAC filter
    hw.cmd_mac()

    # initiator doesn't care about this setting, it always accepts aux
    hw.cmd_auxadv(False)
    # a2:1a:b3:41    41:b3:1a:a2
    # advertiser needs a MAC address
    # hw.random_addr()
    print('设置mac地址为：', args.mac)
    array_mac = args.mac.split(":")
    print("arraymac............")
    print(array_mac)
    reverse_mac = array_mac[::-1]
    print(reverse_mac)
    # arr = []
    mac_str =  "\\x".join(reverse_mac)
    mac_str = "\\x" + mac_str
    print("mac_str.................")
    print(mac_str)
    hw.cmd_setaddr(mac_str)
    # hw.cmd_setaddr(b"\xB3\x55\x44\x44\x55\xB3")

    # advertise roughly every 200 ms
    hw.cmd_adv_interval(200)

    # reset preloaded encrypted connection interval changes
    hw.cmd_interval_preload()

    # zero timestamps and flush old packets
    hw.mark_and_flush()

    # advertising and scan response data
    advData = bytes([
        0x02, 0x01, 0x1A, 0x02, 0x0A, 0x0C, 0x11, 0x07,
        0x64, 0x14, 0xEA, 0xD7, 0x2F, 0xDB, 0xA3, 0xB0,
        0x59, 0x48, 0x16, 0xD4, 0x30, 0x82, 0xCB, 0x27,
        0x05, 0x03, 0x0A, 0x18, 0x0D, 0x18])
    devName = b'NCC Goat'
    scanRspData = bytes([len(devName) + 1, 0x09]) + devName

    # now enter advertiser mode
    hw.cmd_advertise(advData, scanRspData)

    while True:
        msg = hw.recv_and_decode()
        print_message(msg)


def print_message(msg):
    if isinstance(msg, PacketMessage):
        print_packet(msg)
    elif isinstance(msg, DebugMessage) or \
            isinstance(msg, StateMessage) or \
            isinstance(msg, MeasurementMessage):
        print(msg)
    # print()


def print_packet(pkt):
    global client_socket
    # Further decode and print the packet
    dpkt = DPacketMessage.decode(pkt)
    if dpkt.pdutype in ["LL DATA", "LL CONTROL"]:
        print(dpkt)
        if dpkt.pdutype == "LL CONTROL" and dpkt.body[2] == 0x08:  # LL_FEATURE_REQ (0x08)
            hw.cmd_transmit(3, binascii.a2b_hex('090540000000000000'))  # LL_FEATURE_RSP (0x09)
        elif dpkt.pdutype == "LL DATA" and dpkt.body[-3:] == b"\x03\x40\x00":  # Exchange MTU Response (0x03)
            hw.cmd_transmit(2, binascii.a2b_hex('03000400024000'))
        elif dpkt.pdutype == "LL DATA" and dpkt.body[-6:-4] == b"\x01\x00" and dpkt.body[
                                                                               -2:] == b"\x03\x28":  # GATT Characteristic Declaration (0x2803)
            print("================GATT Characteristic Declaration (0x2803)")
            # hw.cmd_transmit(2, binascii.a2b_hex('050004000108')+dpkt.body[-6:-4]+binascii.a2b_hex('0a'))
            hw.cmd_transmit(2, binascii.a2b_hex('1700040009070400020500012a0600020700042a0800020900a62a'))
        elif dpkt.pdutype == "LL CONTROL" and dpkt.body[2] == 0x1:  # LL_CHANNEL_MAP_IND (0x01)
            print("================LL_CHANNEL_MAP_IND,setmap:", dpkt.body[3:8].hex())
            # client_socket.send(b"setmap" + dpkt.body[3:8])
            hw.cmd_setmap(dpkt.body[3:8])
        elif dpkt.pdutype == "LL CONTROL" and dpkt.body[2] == 0:  # LL_CONNECTION_UPDATE_IND (0x00)
            print("===============LL_CONNECTION_UPDATE_IND,PASS===============")
            # hw.cmd_transmit(2, binascii.a2b_hex('0e00040011060100090000180a000a000118'))
        elif dpkt.pdutype == "LL CONTROL" and dpkt.body[2] == 0x0C:  # LL_VERSION_IND (0x0c)
            hw.cmd_transmit(3, binascii.a2b_hex('0c095900a600'))
        elif client_socket != None:
            print("发送：", dpkt.body.hex())
            client_socket.send(dpkt.body)
        print("-" * 60)

    if isinstance(dpkt, ConnectIndMessage):
        hw.decoder_state.cur_aa = dpkt.aa_conn
        hw.decoder_state.last_chan = -1


if __name__ == "__main__":
    main()
