#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import unittest
from test_triplebarrier import TestTripleBarrier
from test_bars import TestBars

def main():
    suite = unittest.TestSuite()

    """"
    suite.addTest(TestTripleBarrier("test_get_daily_vol"))
    suite.addTest(TestTripleBarrier("test_cusum_filter"))
    suite.addTest(TestTripleBarrier("test_get_t1"))
    suite.addTest(TestTripleBarrier("test_get_events"))
    suite.addTest(TestTripleBarrier("test_get_bins"))
    suite.addTest(TestTripleBarrier("test_get_events_w_metalabel"))
    suite.addTest(TestTripleBarrier("test_get_bins_w_metalabel"))
    suite.addTest(TestTripleBarrier("test_w_classifier"))
    """

    suite.addTest(TestBars("test_tick_bars"))
    suite.addTest(TestBars("test_volume_bars"))
    suite.addTest(TestBars("test_dollar_bars"))
    suite.addTest(TestBars("test_analyze_bars"))

    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == "__main__":

    main()