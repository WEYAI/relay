#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: RKE_RELAY
# GNU Radio version: v3.8.5.0-6-g57bd109d

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
from gnuradio.qtgui import Range, RangeWidget

from gnuradio import qtgui

class RKE_RELAY(gr.top_block, Qt.QWidget):

    def __init__(self):
        aparse = argparse.ArgumentParser(description="Connection initiator test script for Sniffle BLE5 sniffer")
        aparse.add_argument("-f", "--ubx_tx_freq", default=None, help="")
        args = aparse.parse_args()
        gr.top_block.__init__(self, "RKE_RELAY")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("RKE_RELAY")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "RKE_RELAY")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.ubx_tx_gain = ubx_tx_gain = 30
        # self.ubx_tx_freq = ubx_tx_freq = 433.92e6
        self.ubx_tx_freq = ubx_tx_freq = args.ubx_tx_freq
        self.ubx_rx_gain = ubx_rx_gain = 30
        self.ubx_rx_freq = ubx_rx_freq = 900e6
        self.samp_rate = samp_rate = 1e6
        self.offset = offset = 300e3
        self.lftx_freq = lftx_freq = 25e6
        self.lfrx_freq = lfrx_freq = 125e3
        self.lf_tx_gain = lf_tx_gain = 10
        self.lf_rx_gain = lf_rx_gain = 10
        self.lf_amp_gain = lf_amp_gain = 5

        ##################################################
        # Blocks
        ##################################################
        self._ubx_tx_gain_range = Range(0, 31, 1, 30, 200)
        self._ubx_tx_gain_win = RangeWidget(self._ubx_tx_gain_range, self.set_ubx_tx_gain, 'tx_gain_range', "counter_slider", int)
        self.top_layout.addWidget(self._ubx_tx_gain_win)
        self._ubx_rx_gain_range = Range(0, 31, 1, 30, 200)
        self._ubx_rx_gain_win = RangeWidget(self._ubx_rx_gain_range, self.set_ubx_rx_gain, 'rx_gain_range', "counter_slider", int)
        self.top_layout.addWidget(self._ubx_rx_gain_win)
        self._lftx_freq_range = Range(10e6, 30e6, 1e6, 25e6, 200)
        self._lftx_freq_win = RangeWidget(self._lftx_freq_range, self.set_lftx_freq, 'lftx_freq', "counter_slider", float)
        self.top_layout.addWidget(self._lftx_freq_win)
        self._lf_tx_gain_range = Range(0, 30, 0.1, 10, 200)
        self._lf_tx_gain_win = RangeWidget(self._lf_tx_gain_range, self.set_lf_tx_gain, 'lf_tx_gain', "counter_slider", float)
        self.top_layout.addWidget(self._lf_tx_gain_win)
        self._lf_rx_gain_range = Range(0, 30, 0.1, 10, 200)
        self._lf_rx_gain_win = RangeWidget(self._lf_rx_gain_range, self.set_lf_rx_gain, 'lf_rx_gain', "counter_slider", float)
        self.top_layout.addWidget(self._lf_rx_gain_win)
        self._lf_amp_gain_range = Range(0, 30, 0.1, 5, 200)
        self._lf_amp_gain_win = RangeWidget(self._lf_amp_gain_range, self.set_lf_amp_gain, 'lf_amp_gain', "counter_slider", float)
        self.top_layout.addWidget(self._lf_amp_gain_win)
        self.uhd_usrp_source_0_0_0 = uhd.usrp_source(
            ",".join(("", "type=b200")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0_0_0.set_center_freq(ubx_rx_freq + offset, 0)
        self.uhd_usrp_source_0_0_0.set_gain(ubx_rx_gain, 0)
        self.uhd_usrp_source_0_0_0.set_antenna('RX2', 0)
        self.uhd_usrp_source_0_0_0.set_samp_rate(samp_rate)
        # No synchronization enforced.
        self.uhd_usrp_source_0_0 = uhd.usrp_source(
            ",".join(("", "type=usrp2")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0_0.set_center_freq(lfrx_freq + offset, 0)
        self.uhd_usrp_source_0_0.set_gain(lf_rx_gain, 0)
        self.uhd_usrp_source_0_0.set_antenna('A', 0)
        self.uhd_usrp_source_0_0.set_samp_rate(samp_rate)
        # No synchronization enforced.
        self.uhd_usrp_sink_0_0_0 = uhd.usrp_sink(
            ",".join(("", "type=b200")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            '',
        )
        self.uhd_usrp_sink_0_0_0.set_center_freq(ubx_tx_freq + offset, 0)
        self.uhd_usrp_sink_0_0_0.set_gain(ubx_tx_gain, 0)
        self.uhd_usrp_sink_0_0_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_sink_0_0_0.set_samp_rate(samp_rate)
        # No synchronization enforced.
        self.uhd_usrp_sink_0_0 = uhd.usrp_sink(
            ",".join(("", "type=usrp2")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            '',
        )
        self.uhd_usrp_sink_0_0.set_center_freq(lftx_freq + offset, 0)
        self.uhd_usrp_sink_0_0.set_gain(lf_tx_gain, 0)
        self.uhd_usrp_sink_0_0.set_antenna('A', 0)
        self.uhd_usrp_sink_0_0.set_samp_rate(samp_rate)
        # No synchronization enforced.
        self.qtgui_freq_sink_x_0_1 = qtgui.freq_sink_c(
            1024, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            lfrx_freq + offset, #fc
            samp_rate, #bw
            "", #name
            1
        )
        self.qtgui_freq_sink_x_0_1.set_update_time(0.10)
        self.qtgui_freq_sink_x_0_1.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0_1.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_1.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_1.enable_grid(False)
        self.qtgui_freq_sink_x_0_1.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0_1.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_1.enable_control_panel(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_1.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_1.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_1.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_1_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_1.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_1_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0_0_0_0 = qtgui.freq_sink_c(
            1024, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            ubx_rx_freq + offset, #fc
            samp_rate, #bw
            "", #name
            1
        )
        self.qtgui_freq_sink_x_0_0_0_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0_0_0_0.set_y_axis(-140, 5)
        self.qtgui_freq_sink_x_0_0_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0_0_0.enable_grid(False)
        self.qtgui_freq_sink_x_0_0_0_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0_0_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0_0_0.enable_control_panel(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0_0_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_0_0_0_win, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.blocks_multiply_const_vxx_1_0 = blocks.multiply_const_cc(lf_amp_gain)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_multiply_const_vxx_1_0, 0), (self.uhd_usrp_sink_0_0, 0))
        self.connect((self.uhd_usrp_source_0_0, 0), (self.blocks_multiply_const_vxx_1_0, 0))
        self.connect((self.uhd_usrp_source_0_0, 0), (self.qtgui_freq_sink_x_0_1, 0))
        self.connect((self.uhd_usrp_source_0_0_0, 0), (self.qtgui_freq_sink_x_0_0_0_0, 0))
        self.connect((self.uhd_usrp_source_0_0_0, 0), (self.uhd_usrp_sink_0_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "RKE_RELAY")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_ubx_tx_gain(self):
        return self.ubx_tx_gain

    def set_ubx_tx_gain(self, ubx_tx_gain):
        self.ubx_tx_gain = ubx_tx_gain
        self.uhd_usrp_sink_0_0.set_gain(self.ubx_tx_gain, 1)
        self.uhd_usrp_sink_0_0_0.set_gain(self.ubx_tx_gain, 0)
        self.uhd_usrp_sink_0_0_0.set_gain(self.ubx_tx_gain, 1)

    def get_ubx_tx_freq(self):
        return self.ubx_tx_freq

    def set_ubx_tx_freq(self, ubx_tx_freq):
        self.ubx_tx_freq = ubx_tx_freq
        self.uhd_usrp_sink_0_0.set_center_freq(self.ubx_tx_freq + self.offset, 1)
        self.uhd_usrp_sink_0_0_0.set_center_freq(self.ubx_tx_freq + self.offset, 0)
        self.uhd_usrp_sink_0_0_0.set_center_freq(self.ubx_tx_freq + self.offset, 1)

    def get_ubx_rx_gain(self):
        return self.ubx_rx_gain

    def set_ubx_rx_gain(self, ubx_rx_gain):
        self.ubx_rx_gain = ubx_rx_gain
        self.uhd_usrp_source_0_0.set_gain(self.ubx_rx_gain, 1)
        self.uhd_usrp_source_0_0_0.set_gain(self.ubx_rx_gain, 0)
        self.uhd_usrp_source_0_0_0.set_gain(self.ubx_rx_gain, 1)

    def get_ubx_rx_freq(self):
        return self.ubx_rx_freq

    def set_ubx_rx_freq(self, ubx_rx_freq):
        self.ubx_rx_freq = ubx_rx_freq
        self.qtgui_freq_sink_x_0_0_0_0.set_frequency_range(self.ubx_rx_freq + self.offset, self.samp_rate)
        self.uhd_usrp_source_0_0.set_center_freq(self.ubx_rx_freq + self.offset, 1)
        self.uhd_usrp_source_0_0_0.set_center_freq(self.ubx_rx_freq + self.offset, 0)
        self.uhd_usrp_source_0_0_0.set_center_freq(self.ubx_rx_freq + self.offset, 1)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_freq_sink_x_0_0_0_0.set_frequency_range(self.ubx_rx_freq + self.offset, self.samp_rate)
        self.qtgui_freq_sink_x_0_1.set_frequency_range(self.lfrx_freq + self.offset, self.samp_rate)
        self.uhd_usrp_sink_0_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_sink_0_0_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0_0_0.set_samp_rate(self.samp_rate)

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset
        self.qtgui_freq_sink_x_0_0_0_0.set_frequency_range(self.ubx_rx_freq + self.offset, self.samp_rate)
        self.qtgui_freq_sink_x_0_1.set_frequency_range(self.lfrx_freq + self.offset, self.samp_rate)
        self.uhd_usrp_sink_0_0.set_center_freq(self.lftx_freq + self.offset, 0)
        self.uhd_usrp_sink_0_0.set_center_freq(self.ubx_tx_freq + self.offset, 1)
        self.uhd_usrp_sink_0_0_0.set_center_freq(self.ubx_tx_freq + self.offset, 0)
        self.uhd_usrp_sink_0_0_0.set_center_freq(self.ubx_tx_freq + self.offset, 1)
        self.uhd_usrp_source_0_0.set_center_freq(self.lfrx_freq + self.offset, 0)
        self.uhd_usrp_source_0_0.set_center_freq(self.ubx_rx_freq + self.offset, 1)
        self.uhd_usrp_source_0_0_0.set_center_freq(self.ubx_rx_freq + self.offset, 0)
        self.uhd_usrp_source_0_0_0.set_center_freq(self.ubx_rx_freq + self.offset, 1)

    def get_lftx_freq(self):
        return self.lftx_freq

    def set_lftx_freq(self, lftx_freq):
        self.lftx_freq = lftx_freq
        self.uhd_usrp_sink_0_0.set_center_freq(self.lftx_freq + self.offset, 0)

    def get_lfrx_freq(self):
        return self.lfrx_freq

    def set_lfrx_freq(self, lfrx_freq):
        self.lfrx_freq = lfrx_freq
        self.qtgui_freq_sink_x_0_1.set_frequency_range(self.lfrx_freq + self.offset, self.samp_rate)
        self.uhd_usrp_source_0_0.set_center_freq(self.lfrx_freq + self.offset, 0)

    def get_lf_tx_gain(self):
        return self.lf_tx_gain

    def set_lf_tx_gain(self, lf_tx_gain):
        self.lf_tx_gain = lf_tx_gain
        self.uhd_usrp_sink_0_0.set_gain(self.lf_tx_gain, 0)

    def get_lf_rx_gain(self):
        return self.lf_rx_gain

    def set_lf_rx_gain(self, lf_rx_gain):
        self.lf_rx_gain = lf_rx_gain
        self.uhd_usrp_source_0_0.set_gain(self.lf_rx_gain, 0)

    def get_lf_amp_gain(self):
        return self.lf_amp_gain

    def set_lf_amp_gain(self, lf_amp_gain):
        self.lf_amp_gain = lf_amp_gain
        self.blocks_multiply_const_vxx_1_0.set_k(self.lf_amp_gain)





def main(top_block_cls=RKE_RELAY, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
