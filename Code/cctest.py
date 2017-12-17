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

p1 = 0.05
p2 = 0.3
p3 = 0.4

def change_mc(initial_mc, vend):
    diff = abs(initial_mc - vend)
    part = initial_mc * p3
    return (diff > part)


def finlt(vbegin, vend, STATE):  # perc es el porcentaje de variación para pertenecer a la misma lt
    diff = abs(vbegin - vend)  # Deriva posible
    umbral1 = vbegin * p1
    umbral2 = vbegin * p2
    umbral3 = vbegin * p3
    if (
        ((diff > umbral1) and (STATE=='P0' or STATE=='P4' or STATE=='P5')) 
    
        or ((diff > umbral2) and (STATE=='P1' or STATE=='P3' or STATE=='P8' or STATE=='P7')) 
        
        or ((diff > umbral3) and (STATE=='P2' or STATE=='P6'))
        ):
        return True
    else:
        return False


def findtype(vbegin, vend, STATE):
    ltype = 0
    diff = vbegin - vend
    percentagePart1 = vbegin * p1
    percentagePart2 = vbegin * p2
    percentagePart3 = vbegin * p3
    
    part1plus = vbegin + percentagePart1
    part2plus = vbegin + percentagePart2
    part3plus = vbegin + percentagePart3
    
    part1minus = vbegin - percentagePart1
    part2minus = vbegin - percentagePart2
    part3minus = vbegin - percentagePart3
    
    if (diff <= 0):  # End > Begin -> SUBE
        diff = abs(diff)
        if (diff <= part1plus and (STATE=='P0' or STATE=='P5' or STATE=='P4')):
            ltype = 1
            STATE='P1'
        elif (diff <= part2plus and (STATE=='P1' or STATE=='P3')):
            ltype = 2
            STATE='P2'
        elif (diff <= part2minus and STATE=='P6'):
            ltype = 7
            STATE='P7'
        elif (diff <= part1minus and (STATE=='P7' or STATE=='P8')):
            ltype = 5
            STATE= 'P5'
        elif (diff <= part3plus and (STATE=='P2')):
            ltype = 0
            STATE= 'P0'
            
    else:  # End < Begin -> BAJA
        
        if (diff <= part1minus and (STATE=='P0' or STATE=='P5' or STATE=='P4')):
            ltype = 8
            STATE='P8'
        elif (diff <= part2minus and (STATE=='P8' or STATE=='P7')):
            ltype = 6
            STATE='P6'
        elif (diff <= part2plus and STATE=='P2'):
            ltype = 3
            STATE='P3'
        elif (diff <= part1plus and (STATE=='P3' or STATE=='P1')):
            ltype = 4
            STATE= 'P4'
        elif (diff <= part3minus and (STATE=='P6')):
            ltype = 0
            STATE= 'P0'

    return ltype, STATE


mypath = 'Top100/'
cryptoconcurrenciesName = [f for f in listdir(mypath) if isfile(join(mypath, f))]

columns = ['Name', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Market Cap']
df = {}
df = pd.DataFrame(columns=columns)

col_time = ['DBegin', 'DEnd', 'Type', 'VBegin', 'VEnd', 'Volume', 'Mean']
dl = {}
dl = pd.DataFrame(columns=col_time)

print cryptoconcurrenciesName
for cryptoName in cryptoconcurrenciesName:
    file = mypath + cryptoName

    cryptoconcurrencies = rp.loadDataCSV(file, target=rp.NONE,
                                         null_target_procedure=rp.DELETE_ROW,
                                         null_procedure=rp.MEAN,
                                         na_values='-')
    df = df.append(cryptoconcurrencies.dataFrame)
    df = df.fillna(cryptoName[0:-4])

monedas = ['Bitcoin']  # ,'Ethereum','Monero']

bamboo = Bamboo('Coins', df, columns, target='Market Cap')
bambooList = rp.divideDataFrame(bamboo, 'Name')
for moneda in monedas:

    for coso in bambooList:
        #        print coso.dataFrame['Name'].iloc[0]
        if coso.dataFrame['Name'].iloc[0] == moneda:
            cdf = coso.dataFrame

            cdf['Date'] = pd.to_datetime(cdf.Date)
            cdf.sort_values(by='Date', inplace=True)

            cdf.index = pd.DatetimeIndex(cdf['Date'])
            # Aplicando el filtro Hodrick-Prescott para separar en tendencia y
            # componente ciclico.
            cdf_ciclo, cdf_tend = sm.tsa.filters.hpfilter(cdf['Market Cap'])
            cdf['tend'] = cdf_tend

            plt.title(moneda)

            print coso.dataFrame

            ###INTENTO DE LINEAS TEMPORALES
            ['DBegin', 'DEnd', 'VBegin', 'VEnd', 'Volume', 'Mean']

            l_temporal = []
            aux_temporal = []
        
            temporal = []
            vacia = True
            volume = 0
            acum = 0
            cont = 0
            initial_mc = cdf['Market Cap'].iloc[0]  # Toma el MC en el momento de entrada a mercado
            ax = None
            
            STATE = 'P0'
            
            for index, row in cdf.iterrows():
                if (vacia):
                    dbegin = row['Date']
                    vbegin = row['Market Cap']
                    vacia = False
                volume = volume + row['Volume']
                acum = acum + row['Market Cap']
                vend = row['Market Cap']
                if ((dbegin != row['Date'])):

                    if (finlt(initial_mc, vend, STATE)):
                        dend = row['Date']
                        cont = cont + 1
                        mean = acum / cont
                        ltype, STATE = findtype(initial_mc, vend, STATE)
                        if STATE == 'P0':
                            initial_mc = vbegin
                            print(initial_mc)
                        temporal = [dbegin, dend, ltype, vbegin, vend, volume, mean, initial_mc]
                        #                    print(temporal)
                        #                    dl.append(temporal)
                        l_temporal.append(temporal)

                        # Inicializacion a 0
                        temporal = []
                        vacia = True
                        volume = 0
                        acum = 0
                        cont = 0

                        aux_temporal.append(
                            cdf[(pd.to_datetime(cdf.index) >= dbegin) & (pd.to_datetime(cdf.index) <= dend)])

            for au in l_temporal:
                print "{}  a {} ".format(pd.to_datetime(au[0]), pd.to_datetime(au[1]))
                l = pd.date_range(pd.to_datetime(au[0]), pd.to_datetime(au[1]))
                

            this_ltemporal = []
            for aux in aux_temporal:
                ax = aux['Market Cap']
                ax2 = aux['Date']
                # Type 1: r (red) Type 2: g (green)
                # Type 3: y (yellow) Type 4: k (black)
                # Type 5: m (magenta) Type 6: c (cyan)
                # Type 7: b (blue) Type 8: w (white)
                for ltemporal in l_temporal:
                    if ax2[0] == ltemporal[0] and ax2[-1] == ltemporal[1]:
                        this_ltemporal = ltemporal
                        break
                typeTemp = this_ltemporal[2]
                if typeTemp==1:
                    ax.plot(c='r', figsize=(15, 8))
                elif typeTemp==2:
                    ax.plot(c='r', figsize=(15, 8))
                elif typeTemp==3:
                    ax.plot(c='b', figsize=(15, 8))
                elif typeTemp==4:
                    ax.plot(c='b', figsize=(15, 8))
                elif typeTemp==5:
                    ax.plot(c='r', figsize=(15, 8))
                elif typeTemp==6:
                    ax.plot(c='b', figsize=(15, 8))
                elif typeTemp==7:
                    ax.plot(c='r', figsize=(15, 8))
                elif typeTemp==8:
                    ax.plot(c='b', figsize=(15, 8))
                elif typeTemp==0:
                    ax.plot(c='y', figsize=(15, 8))
                     
                aux['Market Cap'] = this_ltemporal[7]
    
                aux['Market Cap'].plot(c='k')
