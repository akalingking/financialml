#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import unittest, sys
sys.path.append("..")
from financialml.ch3.cusumfilter import get_daily_vol, cusum_filter_close
from financialml.ch3.triplebarrier import get_events, get_events_w_metalabel, get_t1
from financialml.ch3.bins import get_bins, get_bins_w_metalabel
from financialml.ch3.utils import macd_side, get_close
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score)
import pandas as pd
import numpy as np


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        df = pd.read_csv("../data/Google.csv")
        df.index = pd.DatetimeIndex(df['Date'].values)
        cls._close = df["Close"]

    @classmethod
    def tearDown(cls):
        pass


class TestTripleBarrier(TestBase):
    def test_get_daily_vol(self):
        volatility = get_daily_vol(self._close, span=30)
        print("volatility:\n", volatility[:5])
        self.assertTrue(True)

    def test_cusum_filter(self):
        volatility = get_daily_vol(self._close, span=30)
        t_events = cusum_filter_close(self._close, volatility)
        print("tEvents:\n", t_events[:10])
        self.assertTrue(True)

    def test_get_t1(self):
        volatility = get_daily_vol(self._close, span=30)
        tEvents = cusum_filter_close(self._close, volatility)
        t1 = get_t1(self._close, tEvents)
        print("t1:\n", t1[:5])
        self.assertTrue(True)

    def test_get_events(self):
        volatility = get_daily_vol(self._close, span=30)
        tEvents = cusum_filter_close(self._close, volatility)
        t1 = get_t1(self._close, tEvents, numDays=1)
        # Timestamps barrier was touched for tEvents
        events = get_events(self._close, tEvents, [2, 2], trgt=volatility, t1=t1)
        print("events:\n", events[:5])
        self.assertTrue(True)

    def test_get_bins(self):
        volatility = get_daily_vol(self._close, span=30)
        tEvents = cusum_filter_close(self._close, volatility)
        t1 = get_t1(self._close, tEvents, numDays=1)
        # Timestamps barrier was touched for tEvents
        events = get_events(self._close, tEvents, [2, 2], trgt=volatility, t1=t1)
        x = np.hstack([
            events['side'].values[:, np.newaxis],
            self._close[events.index].values[:, np.newaxis]
        ])
        bins = get_bins(events, self._close)
        print("bins:\n", bins[:5])
        self.assertTrue(True)

    def test_get_events_w_metalabel(self):
        volatility = get_daily_vol(self._close, span=30)
        tEvents = cusum_filter_close(self._close, volatility)
        t1 = get_t1(self._close, tEvents, numDays=1)
        # Timestamps barrier was touched for tEvents
        events = get_events_w_metalabel(self._close, tEvents, [2, 2], trgt=volatility, t1=t1)
        print("events:\n", events[:5])
        self.assertTrue(True)

    def test_get_bins_w_metalabel(self):
        volatility = get_daily_vol(self._close, span=30)
        tEvents = cusum_filter_close(self._close, volatility)
        t1 = get_t1(self._close, tEvents, numDays=1)
        # Timestamps barrier was touched for tEvents
        events = get_events_w_metalabel(self._close, tEvents, [2, 2], trgt=volatility, t1=t1)
        x = np.hstack([
            events['side'].values[:, np.newaxis],
            self._close[events.index].values[:, np.newaxis]
        ])
        bins = get_bins_w_metalabel(events, self._close)
        print("bins:\n", bins[:5])
        self.assertTrue(True)

    def test_w_classifier(self):
        # construct x data
        volatility = get_daily_vol(self._close)
        tEvents = cusum_filter_close(self._close, volatility)
        t1 = get_t1(self._close, tEvents, numDays=1)
        # get signals
        side = macd_side(self._close)
        events = get_events_w_metalabel(
            self._close,
            tEvents=tEvents,
            trgt=volatility,
            ptsl=[1, 1],
            t1=t1,
            side=side
        )

        x = np.hstack([
            events['side'].values[:, np.newaxis],
            self._close.loc[events.index].values[:, np.newaxis]
        ])

        # construct y data
        bins = get_bins_w_metalabel(events, self._close)
        y = bins['bin'].values

        assert(np.shape(x)[0] == np.shape(y)[0])
        train_ratio = 0.75
        data_size = np.shape(x)[0]

        print("X:\n", np.shape(x))
        print("Y:\n", np.shape(y))

        train_size = int(data_size*train_ratio)
        x_train = x[:train_size]
        x_test = x[train_size:]
        y_train = y[:train_size]
        y_test = y[train_size:]

        # Construct Model and train
        model = RandomForestClassifier()
        model.fit(x_train, y_train)

        # predict
        y_pred = model.predict(x_test)
        assert(np.shape(x_test)[0] == np.shape(y_pred)[0])

        # Metrics
        accuracy_score_ = accuracy_score(y_test, y_pred, normalize=True)
        print("Accuracy Score: ", accuracy_score_)
        precision_score_ = precision_score(y_test, y_pred)
        print("Precision Score: ", precision_score_)

        self.assertTrue(True)
