#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pandas as pd
import talib


def macd_side(close):
    """
    generate buy-sell signals using macd
    :param close:
    :return:
    """
    macd, signal, hist = talib.MACD(close.values)
    hist = pd.Series(hist).fillna(1).values
    return pd.Series(2 * ((hist > 0).astype(float) - 0.5), index=close.index[-len(hist):])


def get_close():
    """
    :return: pd.Series
    """
    df = pd.read_csv("../data/Google.csv")
    df.index = pd.DatetimeIndex(df['Date'].values)
    return df["Close"]