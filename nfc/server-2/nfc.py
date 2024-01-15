from PyQt5 import QtCore, QtGui, QtWidgets
import socket
import socketserver
import struct
import sys
from PyQt5.QtCore import QThread

import datetime

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon

HOST = "0.0.0.0"
PORT = 5566


class Worker(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        NFCGateServer((HOST, PORT), NFCGateClientHandler).serve_forever()


class PluginHandler:
    def __init__(self):
        self.plugin_list = []

        for modname in sys.argv[1:]:
            self.plugin_list.append((modname, __import__("plugins.mod_%s" % modname, fromlist=["plugins"])))
            print("Loaded", "mod_%s" % modname)

    def filter(self, client, data):
        for modname, plugin in self.plugin_list:
            if type(data) == list:
                first = data[0]
            else:
                first = data
            first = plugin.handle_data(lambda *x: client.log(*x, tag=modname), first, client.state)
            if type(data) == list:
                data = [first] + data[1:]
            else:
                data = first

        return data


class NFCGateClientHandler(socketserver.StreamRequestHandler):
    def __init__(self, request, client_address, srv):
        super().__init__(request, client_address, srv)

    def log(self, *args, tag="server"):
        self.server.log(*args, origin=self.client_address, tag=tag)

    def setup(self):
        super().setup()

        self.session = None
        self.state = {}
        self.request.settimeout(300)
        self.log("server", "connected")

    def handle(self):
        super().handle()

        while True:
            try:
                msg_len_data = self.rfile.read(5)
            except socket.timeout:
                self.log("server", "Timeout")
                break
            if len(msg_len_data) < 5:
                break

            msg_len, session = struct.unpack("!IB", msg_len_data)
            data = self.rfile.read(msg_len)
            self.log("server", "data:", bytes(data))

            # no data was sent or no session number supplied and none set yet
            if msg_len == 0 or session == 0 and self.session is None:
                break

            # change in session number detected
            if self.session != session:
                # remove from old association
                self.server.remove_client(self, self.session)
                # update and add association
                self.session = session
                self.server.add_client(self, session)

            # allow plugins to filter data before sending it to all clients in the session
            self.server.send_to_clients(self.session, self.server.plugins.filter(self, data), self)

    def finish(self):
        super().finish()

        self.server.remove_client(self, self.session)
        self.log("server", "disconnected")


class NFCGateServer(socketserver.ThreadingTCPServer):
    def __init__(self, server_address, request_handler, bind_and_activate=True):
        self.allow_reuse_address = True
        super().__init__(server_address, request_handler, bind_and_activate)

        self.clients = {}
        self.plugins = PluginHandler()
        self.log("NFCGate server listening on", server_address)

    def log(self, *args, origin="0", tag="server"):
        ar = ""
        for arg in args:
            ar += str(arg)+" "
        ui.receive_signal(str(datetime.datetime.now())+" [" + tag + "] "+origin+" "+ar)

    def add_client(self, client, session):
        if session is None:
            return

        if session not in self.clients:
            self.clients[session] = []

        self.clients[session].append(client)
        client.log("joined session", session)

    def remove_client(self, client, session):
        if session is None or session not in self.clients:
            return

        self.clients[session].remove(client)
        client.log("left session", session)

    def send_to_clients(self, session, msgs, origin):
        if session is None or session not in self.clients:
            return

        for client in self.clients[session]:
            # do not send message back to originator
            if client is origin:
                continue

            if type(msgs) != list:
                msgs = [msgs]

            for msg in msgs:
                client.wfile.write(int.to_bytes(len(msg), 4, byteorder='big'))
                client.wfile.write(msg)

        self.log("Publish reached", len(self.clients[session]) - 1, "clients")


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(600, 400)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.clicked.connect(self.clickButton)
        self.pushButton.setGeometry(QtCore.QRect(100, 50, 81, 31))
        font = QtGui.QFont()
        font.setFamily("华文楷体")
        font.setPointSize(15)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.clicked.connect(self.stopButton)
        self.pushButton_2.setGeometry(QtCore.QRect(380, 50, 81, 31))
        font = QtGui.QFont()
        font.setFamily("华文楷体")
        font.setPointSize(15)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setGeometry(QtCore.QRect(10, 140, 580, 251))
        self.textBrowser.setObjectName("textBrowser")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "NFCServer"))
        Form.setWindowIcon(QIcon("nfc.ico"))
        self.pushButton.setText(_translate("Form", "运  行"))
        self.pushButton_2.setText(_translate("Form", "停  止"))

    def receive_signal(self, text):
        """
        回显至浏览框
        :param text:
        """
        self.textBrowser.append(text)

    def clickButton(self):
        self.textBrowser.append("开始执行")
        t.start()

    def stopButton(self):
        self.textBrowser.append("停止执行")
        t.exit()


if __name__ == "__main__":
    t = Worker()
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(widget)
    widget.show()
    sys.exit(app.exec_())
