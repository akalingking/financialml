#!/usr/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import numbers


def get_daily_vol(close, span=100):
    """
    3.3. Set profit taking and stop-loss limits that are a function of risk
    involved in the bet. Computes daily volatility at intra-day estimation
    points, applying span days to an exponentially weighted moving standard
    deviation.

    3.4 Creates the lower(stop-loss limit) and upper(profit-taking limit) barrier in Triple Barrier Method

    :param close:
    :param span: rolling window for moving average
    :return: pd.Series positive values only
    """
    # sort data index for intra-day
    use_idx = close.index.searchsorted(close.index - pd.Timedelta(days=1))
    use_idx = use_idx[use_idx > 0]

    # Get rid of duplications in index
    use_idx = np.unique(use_idx)

    # get % returns
    prev_idx = pd.Series(close.index[use_idx - 1], index=close.index[use_idx])
    ret = close.loc[prev_idx.index] / close.loc[prev_idx.values].values - 1

    # weighted moving average
    vol = ret.ewm(span=span).std()
    return vol


def cusum_filter(gRaw, h):
    """
    2.5.2.1.
    Quality control method designed to detect a shift in the mean value of a measured
    quantity away from the target value.

    Generates alternating buy and sell signals when an absolute return h is observed relative to
    a previous high or low

    :param gRaw:
    :param h: volatility
    :return: pd.DateTimeIndex
    """
    tEvents, sPos, sNeg = [], 0, 0
    diff = gRaw.diff()
    for i in diff.index[1:]:
        sPos, sNeg = max(0, sPos, + diff.loc[i]), min(0, sNeg + diff.loc[i])
        if sNeg < -h:
            sNeg = 0
            tEvents.append(i)
        elif sPos > h:
            sPos = 0
            tEvents.append(i)

    return pd.DataTimeIndex(tEvents)


def cusum_filter_close(close, h):
    """
    Modified cusum_filter using close
    :param close:
    :param h: volatility
    :return: pd.DateTimeIndex
    """
    tEvents, sPos, sNeg = [], 0, 0
    ret = close.pct_change().dropna()
    diff = ret.diff().dropna()

    if isinstance(h, numbers.Number):
        h = pd.Series(h, index=diff.index)

    h = h.reindex(diff.index, method='bfill')
    h = h.dropna()

    for t in h.index:
        sPos = max(0, sPos + diff.loc[t])
        sNeg = min(0, sNeg + diff.loc[t])
        if sPos > h.loc[t]:
            sPos = 0
            tEvents.append(t)
        elif sNeg < -h.loc[t]:
            sNeg = 0
            tEvents.append(t)

    return pd.DatetimeIndex(tEvents)
