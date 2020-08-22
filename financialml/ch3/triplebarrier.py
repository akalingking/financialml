#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pandas as pd


def get_t1(close, tEvents, numDays=1):
    """
    3.4. Creates the vertical and third barrier (n-bars of position lifetime)
    in Triple Barrier Method.
    :param close:
    :param t_events:
    :param num_days:
    :return:
    """
    t1 = close.index.searchsorted(tEvents + pd.Timedelta(days=numDays))
    t1 = t1[t1 < close.shape[0]]
    t1 = pd.Series(close.index[t1], index=tEvents[:t1.shape[0]])
    return t1


def apply_ptslt1(close, events, ptsl, molecule):
    """
    Triple Barrier
    Profit-taking, stop-loss limit, n-bars

    3.4. Creates Triple Barrier
    :param close: pd.DataFrame
    :param events: 2 columns
        1.t1: timestamp of vertical barrier. nan=disabled
        2.trgt: unit width of horizontal barrier
    :param ptsl: list of 2 non-negative values
        0: width of upper barrier, 0=disabled
        1: width of lower barrier, 0=disabled
    :param molecule: subset of events indices to be processed
    :return: pd.DataFrame of timestamps the barriers were touched
        t1:   Timestamp the barrier was first touched
        trgt: Volatility used to generate the barrier
    """
    # Sample a subset with specific indices
    _events = events.loc[molecule]

    # Time limit
    out = pd.DataFrame(index=_events.index)

    # Set Profit Taking
    if ptsl[0] > 0:
        pt = ptsl[0] * _events["trgt"]
    else:
        # Switch off profit taking
        pt = pd.Series(index=_events.index)
    # Set Stop Loss limit
    if ptsl[1] > 0:
        sl = -ptsl[1] * _events["trgt"]
    else:
        # Switch off stop loss
        sl = pd.Series(index=_events.index)

    # Replace undefined value with the last time index
    time_limits = _events["t1"].fillna(close.index[-1])
    for loc, t1 in time_limits.iteritems():
        df = close[loc:t1]
        # Change the direction depending on the side
        df = (df / close[loc] - 1) * _events.at[loc, 'side']
        # print(df)
        # print(loc, t1, df[df < sl[loc]].index.min(), df[df > pt[loc]].index.min())
        out.at[loc, 'sl'] = df[df < sl[loc]].index.min()
        out.at[loc, 'pt'] = df[df > pt[loc]].index.min()

    out['t1'] = _events['t1'].copy(deep=True)

    return out


def get_events(close, tEvents, ptsl, trgt, minRet=0, numThreads=1, t1=False, side=None):
    """
    3.5 Finds the the first time the barrier is touched

    :param close:
    :param tEvents: timestamps to seed triple-barrier, generated from cusum_filter
    :param ptsl: non-negative float that sets the two barriers, 0=disabled
    :param trgt: absolute returns
    :param minRet: minimum target return required when searching barrier
    :param numThreads:
    :param t1: vertical barriers, false=disabled
    :param side:
    :return:
    """
    # 1. Get target
    trgt = trgt[tEvents]
    trgt = trgt[trgt > minRet]

    # 2. Get t1 (max holding period)
    if t1 is False:
        t1 = pd.Series(pd.NaT, index=tEvents)

    # 3. Form events object, apply stop loss on t1
    side = pd.Series(1., index=trgt.index)
    events = pd.concat({'t1': t1, 'trgt': trgt, 'side': side}, axis=1).dropna(subset=['trgt'])
    df0 = apply_ptslt1(close, events, ptsl, events.index)
    df0_ = df0.dropna(how='all').min(axis=1)
    events['t1'] = df0_

    # if side is None:
    #     events = events.drop('side', axis=1)

    return events


def get_events_w_metalabel(close, tEvents, ptsl, trgt, minRet=0, numThreads=1, t1=False, side=None):
    """
    3.6
    :param close:
    :param tEvents:
    :param ptsl:
    :param trgt:
    :param minRet:
    :param numThreads:
    :param t1:
    :param side:
    :return:
    """
    trgt = trgt[tEvents]
    assert (trgt.shape[0] == tEvents.shape[0])
    trgt = trgt[trgt > minRet]
    # Get time boundary t1
    if t1 is False:
        t1 = pd.Series(pd.NaT, index=tEvents)

    # Define the side
    if side is None:
        side_ = pd.Series(1., index=trgt.index)
        ptsl_ = [ptsl[0], ptsl[0]]
    else:
        side_ = side.loc[trgt.index]
        ptsl_ = ptsl[:2]

    events = pd.concat({'t1': t1, 'trgt': trgt, 'side': side_}, axis=1)
    events = events.dropna(subset=['trgt'])

    df0 = apply_ptslt1(close, events, ptsl_, events.index)

    df0 = df0.dropna(how='all')
    events['t1'] = df0.min(axis=1)

    # if side is None:
    #     events = events.drop('side', axis=1)

    return events

