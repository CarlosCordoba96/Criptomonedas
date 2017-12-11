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
col_time = ['DBegin', 'DEnd', 'VBegin', 'VEnd', 'Volume', 'Mean']
dl={}
dl=pd.DataFrame(columns=col_time)
print cryptoconcurrenciesName
for cryptoName in cryptoconcurrenciesName:
    file = mypath + cryptoName
    
    cryptoconcurrencies = rp.loadDataCSV(file, target=rp.NONE,
                       null_target_procedure = rp.DELETE_ROW, 
                       null_procedure = rp.MEAN,
                       na_values = '-')
    df=df.append(cryptoconcurrencies.dataFrame)
    df=df.fillna(cryptoName[0:-4])
    
    
monedas=['Bitcoin']#,'Ethereum','Monero']

bamboo = Bamboo('Coins', df, columns, target='Market Cap')
bambooList = rp.divideDataFrame(bamboo, 'Name')
for moneda in monedas:
    
    for coso in bambooList:
        #print coso.dataFrame['Name'].iloc[0]
        if coso.dataFrame['Name'].iloc[0] == moneda:
            cdf=coso.dataFrame
            
            cdf['Date'] =pd.to_datetime(cdf.Date)
            cdf.sort_values(by='Date', inplace=True)

            cdf.index = pd.DatetimeIndex(cdf['Date'])            
            # Aplicando el filtro Hodrick-Prescott para separar en tendencia y 
            # componente ciclico.
            cdf_ciclo, cdf_tend = sm.tsa.filters.hpfilter(cdf['Market Cap'])
            cdf['tend'] = cdf_tend


            # graficando la variacion del precio real con la tendencia.
            cdf[['Market Cap', 'tend']].plot(figsize=(10, 8), fontsize=12);
            legend = plt.legend()
            plt.title(moneda)
            legend.prop.set_size(14);
            
            #Añadido por moi
            descomposition = sm.tsa.seasonal_decompose(cdf['Market Cap'],
                                                       model = 'additive', freq = 30)
            fig = descomposition.plot()

            # Ejemplo de descomposición de serie de tiempo
            descomposicion = sm.tsa.seasonal_decompose(cdf['Market Cap'],
                                                  model='additive', freq=365)  
            fig = descomposicion.plot()            

            variacion_diaria = cdf['Close'] / cdf['Close'].shift(1) - 1
            cdf['var_diaria'] = variacion_diaria
            cdf['var_diaria'][:5]
            
            # modelo ARIMA sobre variación diaria
            modelo = sm.tsa.ARIMA(cdf['var_diaria'].iloc[1:], order=(1, 0, 0))  
            resultados = modelo.fit(disp=-1)  
            cdf['prediccion'] = resultados.fittedvalues  
            plot = cdf[['var_diaria', 'prediccion']].plot(figsize=(10, 8)) 

            print coso.dataFrame
            
####INTENTO DE LINEAS TEMPORALES
#            ['DBegin', 'DEnd', 'VBegin', 'VEnd', 'Volume', 'Mean']
            
            temporal = []
            vacia = True
            volume = 0
            acum = 0
            for index, row in cdf.iterrows():
                if (vacia):
                    dbegin = row['Date']
                    vbegin = row['Market Cap']
                    vacia = False
                volume = volume + row['Volume']
                acum = acum + row['Market Cap']
                if (finlt()):
                    dend = row['Date']
                    vend = row['Market Cap']
                    cont = dend - dbegin
                    mean = acum/cont
                    temporal = [dbegin,dend,vbegin,vend,volume,mean]
                    dl.append(temporal)
                    
                    #Inicializacion a 0
                    temporal = []
                    vacia = True
                    volume = 0
                    acum = 0
                    
                    
                    
                    
                
                
                
                
                