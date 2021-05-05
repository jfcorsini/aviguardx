#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Prototype Jr
# GNU Radio version: v3.8.2.0-102-gcc5a816b

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import osmosdr
import time
import os


class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Prototype Jr")

        ##################################################
        # HERE IS AVIGUARDX CODE
        ##################################################
        folder_name = sys.argv[1]
        results_dir = os.path.join(os.getcwd(), "data")
        if not os.path.isdir(results_dir):
            os.makedirs(results_dir)

        savedir = os.path.join(os.getcwd(), "data", folder_name)
        if not os.path.isdir(savedir):
            os.makedirs(savedir)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2400000
        self.gain_1 = gain_1 = 10
        self.gain_0 = gain_0 = 10

        ##################################################
        # Blocks
        ##################################################
        self.rtlsdr_source_1 = osmosdr.source(
            args="numchan=" + str(1) + " " + 'rtl=1'
        )
        self.rtlsdr_source_1.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_1.set_sample_rate(samp_rate)
        self.rtlsdr_source_1.set_center_freq(560000000, 0)
        self.rtlsdr_source_1.set_freq_corr(0, 0)
        self.rtlsdr_source_1.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_1.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_1.set_gain_mode(False, 0)
        self.rtlsdr_source_1.set_gain(gain_1, 0)
        self.rtlsdr_source_1.set_if_gain(20, 0)
        self.rtlsdr_source_1.set_bb_gain(20, 0)
        self.rtlsdr_source_1.set_antenna('1', 0)
        self.rtlsdr_source_1.set_bandwidth(0, 0)
        self.rtlsdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + 'rtl=0'
        )
        self.rtlsdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0.set_center_freq(560000000, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(gain_0, 0)
        self.rtlsdr_source_0.set_if_gain(20, 0)
        self.rtlsdr_source_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0.set_antenna('0', 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_cc(128)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(128)
        self.blocks_file_sink_1 = blocks.file_sink(
            gr.sizeof_char*1, os.path.join(savedir, 'output1'), False)
        self.blocks_file_sink_1.set_unbuffered(False)
        self.blocks_file_sink_0 = blocks.file_sink(
            gr.sizeof_char*1, os.path.join(savedir, 'output2'), False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_interleaved_char_1 = blocks.complex_to_interleaved_char(
            False)
        self.blocks_complex_to_interleaved_char_0 = blocks.complex_to_interleaved_char(
            False)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_interleaved_char_0, 0),
                     (self.blocks_file_sink_1, 0))
        self.connect((self.blocks_complex_to_interleaved_char_1, 0),
                     (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0),
                     (self.blocks_complex_to_interleaved_char_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0),
                     (self.blocks_complex_to_interleaved_char_1, 0))
        self.connect((self.rtlsdr_source_0, 0),
                     (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.rtlsdr_source_1, 0),
                     (self.blocks_multiply_const_vxx_1, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)
        self.rtlsdr_source_1.set_sample_rate(self.samp_rate)

    def get_gain_1(self):
        return self.gain_1

    def set_gain_1(self, gain_1):
        self.gain_1 = gain_1
        self.rtlsdr_source_1.set_gain(self.gain_1, 0)

    def get_gain_0(self):
        return self.gain_0

    def set_gain_0(self, gain_0):
        self.gain_0 = gain_0
        self.rtlsdr_source_0.set_gain(self.gain_0, 0)


def main(top_block_cls=top_block, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Running GNURadio script')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
