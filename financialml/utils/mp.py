#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pandas as pd
import multiprocessing as mp
import datetime as dt
import numpy as np
import time
import sys

def lin_parts(numAtoms, numThreads):
    # partition of atoms with a single loop
    parts = np.linspace(0, numAtoms, min(numThreads,numAtoms)+1)
    parts = np.ceil(parts).astype(int)
    return parts

def nested_parts(numAtoms, numThreads, upperTriang=False):
    # partition of atoms with an inner loop
    parts,numThreads_ = [0],min(numThreads, numAtoms)
    for num in range(numThreads_):
        part = 1+4*(parts[-1]**2+parts[-1]+numAtoms*(numAtoms+1.)/numThreads_)
        part = (-1+part**.5)/2.
        parts.append(part)
    parts = np.round(parts).astype(int)
    if upperTriang: # the first rows are heaviest
        parts = np.cumsum(np.diff(parts)[::-1])
        parts = np.append(np.array([0]),parts)
    return parts

def expand_call(kwargs):
    # Expand the arguments of a callback function, kargs['func']
    func = kwargs['func']
    del kwargs['func']
    out = func(**kwargs)
    return out

def process_jobs_(jobs):
    # sequential
    out = []
    for job in jobs:
        out_ = expand_call(job)
        out.append(out_)
    return out

def report_progress(jobNum, numJobs, time0, task):
    # Report progress as asynch jobs are completed
    msg = [float(jobNum)/numJobs, (time.time()-time0)/60.]
    msg.append(msg[1]*(1/msg[0]-1))
    timeStamp = str(dt.datetime.fromtimestamp(time.time()))
    msg = timeStamp + ' ' + str(round(msg[0]*100,2))+'% ' + task + ' done after '+ \
        str(round(msg[1],2))+' minutes. Remaining '+str(round(msg[2],2))+' minutes.'
    if jobNum < numJobs:
        sys.stderr.write(msg+'\r')
    else:
        sys.stderr.write(msg+'\n')
    return

def process_jobs(jobs, task=None, numThreads=2):
    # jobs must contain a 'func' callback, for expand_call
    if task is None: task = jobs[0]['func'].__name__
    pool = mp.Pool(processes=numThreads)
    outputs, out, time0 = pool.imap_unordered(expand_call,jobs),[],time.time()
    # Process async output, report progress
    for i,out_ in enumerate(outputs,1):
        out.append(out_)
        report_progress(i, len(jobs), time0, task)
    pool.close()
    pool.join() 
    return out

def mp_pandas_obj(func, pdObj, numThreads=2, mpBatches=1, linMols=True, **kwargs):
    '''
    + func: function to be parallelized. Returns a DataFrame
    + pdObj[0]: Name of argument used to pass the molecule
    + pdObj[1]: List of atoms that will be grouped into molecules
    + kwds: any other argument needed by func
    + ret: dataframe or series
    Example: df = mp_pandas_obj(func, ('molecule',df0.index), 2, **kwargs)
    '''
    #if linMols:parts=lin_parts(len(argList[1]),numThreads*mpBatches)
    #else:parts=nested_parts(len(argList[1]),numThreads*mpBatches)
    if linMols:
        parts = lin_parts(len(pdObj[1]),numThreads*mpBatches)
    else:
        parts = nested_parts(len(pdObj[1]),numThreads*mpBatches)

    jobs=[]
    for i in range(1,len(parts)):
        job = {pdObj[0]:pdObj[1][parts[i-1]:parts[i]],'func':func}
        job.update(kwargs)
        jobs.append(job)
    
    if numThreads == 1:
        out = process_jobs_(jobs)
    else: 
        out = process_jobs(jobs, numThreads=numThreads)
    
    if isinstance(out[0], pd.DataFrame):
        df0 = pd.DataFrame()
    elif isinstance(out[0],pd.Series):
        df0 = pd.Series()
    else:
        return out
    
    for i in out:
        df0 = df0.append(i)
    
    df0 = df0.sort_index()

    return df0

