#!/usr/bin/python3
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tqdm import tqdm

def load_bars(path):
    cols = list(map(str.lower, ['Date', 'Time', 'Price', 'Bid', 'Ask', 'Size']))
    df = (pd.read_csv(path, header=None)
            .rename(columns=dict(zip(range(len(cols)), cols)))
            .assign(dates=lambda df: (pd.to_datetime(df['date'] + df['time'], format='%m/%d/%Y%H:%M:%S')))
            .assign(v=lambda df: df['size'])  # volume
            .assign(dv=lambda df: df['price'] * df['size'])  # dollar volume
            .drop(['date', 'time'], axis=1)
            .set_index('dates')
            .drop_duplicates())
    return df

def mad_outlier(y, threshold=3.):
    """
    Compute outliers based on mad
    args
        y: assumed to be array with shape (N,1)
        thresh: float()
    returns
        array index of outliers
    """
    median = np.median(y)
    diff = np.sum((y - median) ** 2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > threshold

""" Tick Bars """
def get_tick_bars_idx(df, price_col, m):
    """ :param df: pd.DataFrame
        :param price_col:
        :param m: ticks threshold
        :return: indices """
    t = df[price_col]
    ts = 0
    idx = []
    for i, x in enumerate(tqdm(t)):
        ts += 1
        if ts >= m:
            idx.append(i)
            ts = 0
    return idx

def get_tick_bars(df, price_col, m):
    """
    :param df: bid-ask data with price
    :param price_col:
    :param m: tick size threshold
    :return:
    """
    idx = get_tick_bars_idx(df, price_col, m)
    return df.iloc[idx].drop_duplicates()

def get_sample_data(ref, sub, price_col, date):
    xdf = ref[price_col].loc[date]
    xtdf = sub[price_col].loc[date]
    return xdf, xtdf


def plot_sample_data(ref, sub, bar_type, *args, **kwds):
    f, axes = plt.subplots(3, sharex=True, sharey=True, figsize=(10, 7))
    ref.plot(*args, **kwds, ax=axes[0], label='price')
    sub.plot(*args, **kwds, ax=axes[0], marker='X', ls='', label=bar_type)
    axes[0].legend();

    ref.plot(*args, **kwds, ax=axes[1], label='price', marker='o')
    sub.plot(*args, **kwds, ax=axes[2], ls='', marker='X',
             color='r', label=bar_type)

    for ax in axes[1:]: ax.legend()
    plt.tight_layout()

def get_ohlc(ref, sub):
    """
    :param ref:
    :param sub:
    :return:
    """
    ohlc = []
    for i in tqdm(range(sub.index.shape[0]-1)):
        start, end = sub.index[i], sub.index[i+1]
        tmp_ref = ref.loc[start:end]
        max_px, min_px = tmp_ref.max(), tmp_ref.min()
        o, h, l, c = sub.iloc[i], max_px, min_px, sub.iloc[i+1]
        ohlc.append((end, start, o, h, l, c))
    cols = ["end", "start", "open", "high", "low", "close"]
    return pd.DataFrame(ohlc, columns=cols)

""" Volume bars """
def volume_bars_idx(df, volume_column, m):
    """
    :param df:
    :param volume_columm:
    :param m: threshold
    :return: list of indices
    """
    t = df[volume_column]
    ts = 0
    idx = []
    for i, x in enumerate(tqdm(t)):
        ts += x
        if ts >= m:
            idx.append(i)
            ts = 0
    return idx

def get_volume_bars(df, volume_column, m):
    """
    :param df:
    :param volume_column:
    :param m:
    :return:
    """
    idx = volume_bars_idx(df, volume_column, m)
    return df.iloc[idx].drop_duplicates()

""" Dollar Bars"""
def dollar_bars_idx(df, dv_column, m):
    """
    :param df:
    :param dv_column:
    :param m:
    :return:
    """
    t = df[dv_column]
    ts = 0
    idx = []
    for i, x in enumerate(tqdm(t)):
        ts += x
        if ts >= m:
            idx.append(i)
            ts = 0
    return idx

def get_dollar_bars(df, dv_column, m):
    """
    :param df:
    :param dv_column:
    :param m:
    :return:
    """
    idx = dollar_bars_idx(df, dv_column, m)
    return df.iloc[idx].drop_duplicates()
