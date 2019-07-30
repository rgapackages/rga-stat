#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 11:53:59 2019

@author: arpitaggarwal
"""

import pandas as pd
import numpy as np
import datetime
import argparse
import re
import math
import os.path
#import functools
#import operator

#import RGA libraries
"""
import rga_stat
import rga_files
import rga_enum
import rga_plot
import rga_feature
"""
import warnings
warnings.filterwarnings('ignore')
#%%
"""
import importlib
importlib.reload(rga_files)
"""
def printt():
    print("FINALLY WORKING")
    
def ecdf(data):
    """Compute ECDF for a one-dimensional array of measurements."""
    # Number of data points: n
    n = len(data)
    # x-data for the ECDF: x
    x = np.sort(data)
    # y-data for the ECDF: y
    y = np.arange(1, n+1) / n
    return x, y

def process_file(f,sel_cols = [],log=True):
    if log:
        print("Working on: ", f)
    if len(sel_cols):
        df = pd.read_csv(f,encoding='latin-1',usecols=sel_cols)
    else:
        df = pd.read_csv(f,encoding='latin-1')
    #df = remove_duplicate(f,df,f)
    #remove_internal_id(f,df,f)
    #df = select_country(f, df, f, country = rga_enum.country_interested)
    return df
 #%%
 
def clean_age(age_loc = "", df_age = ""):
    if os.path.isfile(age_loc):
        df_age = pd.read_csv(age_loc)
    #df_age = df_age.loc[df_age['install_date'] != "-1"]
    df_age = df_age.loc[df_age['age'] > -1]
    df_age['OCD']= pd.to_datetime(df_age['OCD'])
    return df_age

def generate_datelist(sd ="", ed = ""):
    if sd == "":
        print("*********** SAMPLE ***********")
        print("__________________________________")
        print("Enter start date: Format- %y-%m-%d")
        sd = input()
        print("Enter end date: Format- %y-%m-%d")
        ed = input()    
    start = datetime.datetime.strptime(sd, "%Y-%m-%d")
    end = datetime.datetime.strptime(ed, "%Y-%m-%d")
    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]
    return date_generated

def daywise_cum_revenue(date_generated, df_age,location, size = 0.8):
    i = 0
    for date1 in date_generated:   
        var_start = date1.strftime("%Y-%m-%d") 
        var_end = date1.strftime("%Y-%m-%d")
        var_end = datetime.datetime.strptime(var_end, "%Y-%m-%d").date()
        var_end = var_end + datetime.timedelta(days=7)
        var_end = var_end.strftime("%Y-%m-%d")
        df_age_temp = df_age.loc[df_age['transaction_no'] == 1]
        df_age_temp = df_age_temp.loc[df_age['OCD'] == var_start]
        df_age_temp = df_age_temp[['DEVICE_ID']]        
        df_age_temp1 = df_age.loc[df_age['OCD'] >= var_start]
        df_age_temp1 = df_age_temp1.loc[df_age_temp1['OCD'] <= var_end]
        table_revenue = pd.pivot_table(df_age_temp1, values='Revenue_USD', index=['DEVICE_ID'], aggfunc=np.sum)
        table_revenue.to_csv(location +  "temp.csv")
        table_revenue1 = pd.read_csv(location +  "temp.csv")
        keys = list(["DEVICE_ID"])
        i1 = table_revenue1.set_index(keys).index
        i2 = df_age_temp.set_index(keys).index
        table_revenue1 = table_revenue1[i1.isin(i2)]
        table_revenue1 = table_revenue1.sample(frac = size)
        table_revenue1.to_csv(location + str(i) +  ".csv")
        i= i+1
    location_rev =[]
    i=0
    for date1 in date_generated:
        location_rev.append(location + str(i) + ".csv")
        i =i+1
    t_a = [process_file(d) for d in location_rev]
    t_a = pd.concat(t_a)
    return t_a

def generate_normaldist_sample(t_a, size = 100, sample_size = 50 ):
    j=0       
    cols = ["Revenue_USD"]
    lst =[]
    while j<int(size):
        t1 = t_a.sample(n = int(sample_size))
        total = t1['Revenue_USD'].sum()
        lst.append([total])
        j= j+1
    df_samplea = pd.DataFrame(lst, columns=cols)    
    #t_a.to_csv(outp,index=False)
    #df_samplea.to_csv(outp1, index = False)
    return df_samplea

def ztest_independent(df_samplea, df_sampleb):
    if isinstance(df_samplea, pd.DataFrame):
        print("INPUT: Dataframe")
    else:    
        df_samplea = pd.DataFrame(df_samplea)
    if isinstance(df_sampleb, pd.DataFrame):
        print("INPUT: Dataframe")
    else:    
        df_sampleb = pd.DataFrame(df_sampleb)    
    t_a_mean = df_samplea["Revenue_USD"].mean()
    t_b_mean = df_sampleb["Revenue_USD"].mean()
    t_a_std = df_samplea.loc[:,"Revenue_USD"].std()
    t_b_std = df_sampleb.loc[:,"Revenue_USD"].std()
    t_a_size = df_samplea.shape[0]
    t_b_size = df_sampleb.shape[0]
    std_err= math.sqrt((((t_a_std**2)/t_a_size) + ((t_b_std**2)/t_b_size)))
    z_value = (t_a_mean - t_b_mean)/std_err
    print("###########################################")
    print("-------------------------------------------")
    print("############## RESULTS ####################")
    print("-------------------------------------------")   
    """print(f"t_a_mean : {t_a_mean}")   
    print(f"t_b_mean : {t_b_mean}")
    print(f"t_a_std : {t_a_std}")
    print(f"t_b_std : {t_b_std}")
    print(f"t_a_size : {t_a_size}")
    print(f"t_b_size : {t_b_size}")
    print(f"std_err : {std_err}")
    print(f"z_value : {z_value}")"""
    dictionary = pd.DataFrame({'DESCRIPTION': ['SAMPLE A (mean)', 'SAMPLE B (mean)', 'SAMPLE A (std. Dev)', 'SAMPLE B (std. Dev)', 'SAMPLE A (Size)', 'SAMPLE B (Size)' , 'STANDARD ERROR' , 'Z_VALUE'],
                    'VALUES': [t_a_mean, t_b_mean, t_a_std, t_b_std, t_a_size,t_b_size, std_err, z_value]})
    print(dictionary)
    return dictionary, int(z_value)

def check_significance(z_value):
    if z_value > 1.96:
        print("SIGNIFICANTLY DIFFERENT")
    elif z_value < -1.96:
        print("SIGNIFICANTLY DIFFERENT")
    else:
        print("INSIGNIFICANT") 
