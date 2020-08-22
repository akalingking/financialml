#!/usr/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd


def get_bins(events, close):
    """
    Construct labels
    :param events: pd.DateTimeIndex when barrier was touched
    :param close:
    :return: out: pd.DataFrame
        ret: realized return
        bin {-1,0,1}
    """
    # Prices aligned with events
    events = events.dropna(subset=['t1'])
    px = events.index.union(events['t1'].values).drop_duplicates()
    px = close.reindex(px, method='bfill')

    # Create output object
    out = pd.DataFrame(index=events.index)
    out['ret'] = px.loc[events['t1'].values].values / px.loc[events.index] - 1.
    out['bin'] = np.sign(out['ret'])

    return out


def get_bins_w_metalabel(events, close):
    """
    Construct labels
    :param events: pd.DateTimeIndex when barrier was touched
    :param close:
    :return: out: pd.DataFrame
        ret: realized return
        bin {-1,0,1}
    """
    # Prices aligned with events
    events = events.dropna(subset=['t1'])
    px = events.index.union(events['t1'].values).drop_duplicates()
    px = close.reindex(px, method='bfill')

    # Create output object
    out = pd.DataFrame(index=events.index)
    out['ret'] = px.loc[events['t1'].values].values / px.loc[events.index] - 1.

    if 'side' in events:
        out['ret'] *= events['side']

    out['bin'] = np.sign(out['ret'])

    if 'side' in events:
        out.loc[out['ret'] <= 0, 'bin'] = 0

    return out