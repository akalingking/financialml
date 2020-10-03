#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import unittest, sys
sys.path.append("..")
from financialml.ch1.bars import (
    load_bars,
    mad_outlier,
    get_ohlc,
    get_tick_bars,
    get_volume_bars,
    get_dollar_bars,
    get_sample_data,
    plot_sample_data)
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from multiprocessing import Pool, cpu_count


class TestBase(unittest.TestCase):
    _data_filepath = "../data/IVE_tickbidask.txt"
    _data_filepath_parq = "../data/IVE_tickbidask_clean.parq"

    @classmethod
    def setUpClass(cls):
        file = Path(cls._data_filepath_parq)
        if file.exists():
            cls._data = pd.read_parquet(file)
        else:
            # load from raw data
            path = Path(cls._data_filepath)
            data = load_bars(path)
            # sns.boxplot(data.price)
            # plt.show()
            # clean data
            outliers = mad_outlier(data.price.values.reshape(-1, 1))
            cls._data = data.loc[~outliers]
            # save to compact format
            path_parq_clean = Path(cls._data_filepath_parq)
            cls._data.to_parquet(path_parq_clean)

        cls._sample_date = "2009-10-01"
        cls._m = 100
        cls._pool = Pool(cpu_count())
        cls._plot_enable = True

    @classmethod
    def tearDownClass(cls):
        try:
            cls._pool.close()
            cls._pool.join()
        except Exception as e:
            print(str(e))

    def count_bars(self, df, price_col='price'):
        return df.groupby(pd.Grouper(freq='1W'))[price_col].count()
        #return df.resample('1W')[price_col].count()

    def scale(self, df):
        return (df-df.min())/(df.max()-df.min())

""" Plotters """
class PlotTicks(object):
    def __init__(self, fname=None):
        object.__init__(self)
        self._fname = fname

    def __call__(self, xdf, xtdf):
        if self._fname is not None:
            plot_sample_data(xdf, xtdf, 'tick bar', alpha=0.5, markersize=7)
            plt.savefig(self._fname)

class PlotTickCounts(object):
    def __call__(self, tc, vc, dc):
        f, ax = plt.subplots(figsize=(10,7))
        tc.plot(ax=ax, ls='-', label='tick count')
        vc.plot(ax=ax, ls='--', label='volume count')
        dc.plot(ax=ax, ls='-.', label='dollar count')
        ax.set_title('scaled bar counts')
        ax.legend()
        plt.savefig("../data/tick_counts.pdf")

class TestBars(TestBase):
    #@unittest.skip
    def test_tick_bars(self):
        t_bars = get_tick_bars(self._data, "price", m=self._m)
        xdf, xtdf = get_sample_data(self._data, t_bars, "price", self._sample_date)
        if self._plot_enable:
            self._pool.apply_async(PlotTicks("../data/ch1_tbars.pdf"), (xdf, xtdf)).get()

        tick_bars_ohlc = get_ohlc(self._data, t_bars)
        print(tick_bars_ohlc.head())

        self.assertTrue(True)

    def test_volume_bars(self):
        m = 1000
        v_bars = get_volume_bars(self._data, "v", m)
        xdf, xtdf = get_sample_data(self._data, v_bars, 'price', self._sample_date)
        print(f'xdf shape: {xdf.shape}, xtdf shape: {xtdf.shape}')
        if self._plot_enable:
            self._pool.apply_async(PlotTicks("../data/ch1_vbars.pdf"), (xdf, xtdf)).get()
        self.assertTrue(True)

    def test_dollar_bars(self):
        m = 1000000
        d_bars = get_dollar_bars(self._data, "dv", m)
        xdf, xtdf = get_sample_data(self._data, d_bars, 'price', self._sample_date)
        print(f'xdf shape: {xdf.shape}, xtdf shape: {xtdf.shape}')
        if self._plot_enable:
            self._pool.apply_async(PlotTicks("../data/ch1_dbars.pdf"), (xdf, xtdf)).get()
        self.assertTrue(True)

    #@unittest.skip
    def test_analyze_bars(self):
        t_bars = get_tick_bars(self._data, "price", m=self._m)
        v_bars = get_volume_bars(self._data, "price", m=self._m)
        d_bars = get_dollar_bars(self._data, "price", m=self._m)
        tc = self.scale(self.count_bars(t_bars))
        vc = self.scale(self.count_bars(v_bars))
        dc = self.scale(self.count_bars(d_bars))
        dfc = self.scale(self.count_bars(self._data))

        if self._plot_enable:
           self._pool.apply_async(PlotTickCounts(), (tc, vc, dc)).get()

        # stable bar counts
        bar_types = ['tick', 'volume', 'dollar', 'df']
        bar_std = [tc.std(), vc.std(), dc.std(), dfc.std()]
        counts = (pd.Series(bar_std, index=bar_types))
        counts = counts.sort_values()
        print(counts)
        self.assertTrue(True)
