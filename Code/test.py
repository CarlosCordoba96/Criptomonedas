# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 15:53:15 2017

@author: Edu
"""

import RedPandas as rp
import pandas as pd
import datetime
from os import listdir
from os.path import isfile, join
mypath = 'Top100/'
cryptoconcurrenciesName = [f for f in listdir(mypath) if isfile(join(mypath, f))]


print cryptoconcurrenciesName
for cryptoName in cryptoconcurrenciesName:
    file = mypath + cryptoName
    cryptoconcurrencies = rp.loadDataCSV(file, target=rp.NONE,
                       null_target_procedure = rp.DELETE_ROW, 
                       null_procedure = rp.MEAN,
                       na_values = '-')
    
    #cryptoconcurrencies.dataFrame['Volume'].astype(float)
    #cryptoconcurrencies.dataFrame['Market Cap'].astype(float)
    df=cryptoconcurrencies.dataFrame
    df['Date'] = pd.to_datetime(df['Date'])
    #df['Date']=df['Date'].apply((lambda x:datetime.datetime.strptime(str(x),'%Y%m%d:%H:%M:%S'))) 
   # print(' ')
    #print(cryptoName)
    #cryptoconcurrencies.showBasicInfo()