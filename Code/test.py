# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 15:53:15 2017

@author: Edu
"""

import RedPandas as rp
import pandas as pd
from Bamboo import Bamboo
import numpy as np
import datetime
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import statsmodels.api as sm

mypath = 'Top100/'
cryptoconcurrenciesName = [f for f in listdir(mypath) if isfile(join(mypath, f))]

columns = ['Name','Date','Open', 'High','Low','Close','Volume','Market Cap']
df={}
df=pd.DataFrame(columns=columns)
print cryptoconcurrenciesName
for cryptoName in cryptoconcurrenciesName:
    file = mypath + cryptoName
    
    cryptoconcurrencies = rp.loadDataCSV(file, target=rp.NONE,
                       null_target_procedure = rp.DELETE_ROW, 
                       null_procedure = rp.MEAN,
                       na_values = '-')
    df=df.append(cryptoconcurrencies.dataFrame)
    df=df.fillna(cryptoName[0:-4])
    
    
monedas=['Bitcoin','Ethereum','Monero']

bamboo = Bamboo('Coins', df, columns, target='Market Cap')
bambooList = rp.divideDataFrame(bamboo, 'Name')
for moneda in monedas:
    
    for coso in bambooList:
        #print coso.dataFrame['Name'].iloc[0]
        if coso.dataFrame['Name'].iloc[0] ==moneda:
            cdf=coso.dataFrame
            
            cdf['Date'] =pd.to_datetime(cdf.Date)
            cdf.sort_values(by='Date', inplace=True)
            
            # Aplicando el filtro Hodrick-Prescott para separar en tendencia y 
            # componente ciclico.
            cdf_ciclo, cdf_tend = sm.tsa.filters.hpfilter(cdf['Market Cap'])
            cdf['tend'] = cdf_tend


            # graficando la variacion del precio real con la tendencia.
            cdf[['Market Cap', 'tend']].plot(figsize=(10, 8), fontsize=12);
            legend = plt.legend()
            legend.prop.set_size(14);

            print coso.dataFrame