#!/usr/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd


def get_bins(events, close):
    """
    Construct labels
    :param events: pd.DateTimeIndex when barrier was touched
        - index: events start time
        - events['t1']: events end time
    :param close:
    :return: out: pd.DataFrame
        out['ret']: realized return
        out['bin']: sign of return
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
        - index: events start time
        - events['t1']: events end time
        - events['trgt]: events target
        - events['side]: (optional) implies the algo's position side
        case 1: side not in events: bin is (-1,1) <- label by price action
        case 2: side in events: bin is (0,1) <- label by pnl (meta-labeling)
    :param close:
    :return: out: pd.DataFrame
        out['ret']: realized return
        out['bin']: (see above)
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
