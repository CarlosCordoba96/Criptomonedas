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

def clustering(cases):
        
    import matplotlib.pyplot as plt
    import numpy
    from scipy import cluster
    from sklearn import preprocessing 
    import sklearn.neighbors
    
    # Loads the data into array 'cases'
     
    # Normalization of the data to work with it in clustering
    min_max_scaler = preprocessing.MinMaxScaler()
    norm_cases = min_max_scaler.fit_transform(cases)
    from sklearn.decomposition import PCA
    estimator = PCA (n_components = 2)
    X_pca = estimator.fit_transform(norm_cases)
    plt.plot(X_pca[:,0], X_pca[:,1],'x')
    
    # Computing the similarity matrix. Here the distance function that we selected is chosen.
    dist = sklearn.neighbors.DistanceMetric.get_metric('euclidean') 
    matsim = dist.pairwise(norm_cases)
    avSim = numpy.average(matsim)
    print "%s\t%6.2f" % ('Average Distance', avSim)
    
    # Creates the dendrogram and plots it
    cut = 7     #This variable represents where the separation of the elements into clusters starts. From that point to the bottom of the plot
    clusters = cluster.hierarchy.linkage(matsim, method = 'complete')
    cluster.hierarchy.dendrogram(clusters, color_threshold = cut)
    plt.show()
    
    # Characterization of the data
    labels = cluster.hierarchy.fcluster(clusters, cut , criterion = 'distance')
    print 'Nº of clusters %d' % (len(set(labels)))     #Gives the number of clusters as it is represented
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    print('Estimated number of clusters: %d' % n_clusters_)
    
    # Calculates the mean of each of the attributes for the elements related to each cluster. Prints every mean in the attributes for every cluster
#    for c in range(1,n_clusters_+1):
#        s = ''
#        print 'Group', c
#        for i in range(99):
#            column = [row[i] for j,row in enumerate(cases) if labels[j] == c]
#            if len(column) != 0:
#                s = "%s,%s" % (s,numpy.mean(column))
#        print s
    
    # Representation of all the elements in the dataset into a PCA. Each color into that plot tells the cluster where the elements belong
    colors = numpy.array([x for x in 'bgrcmykbgrcmykbgrcmykbgrcmyk'])
    colors = numpy.hstack([colors] * 20)
    numbers = numpy.arange(len(X_pca))
    fig, ax = plt.subplots()
    for i in range(len(X_pca)):
        plt.text(X_pca[i][0], X_pca[i][1], numbers[i], color=colors[labels[i]])
    plt.xlim(-1, 2)
    plt.ylim(-0.4, 0.8)
    ax.grid(True)
    fig.tight_layout()
    plt.show()


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

col_coins = ['Cryptocurrency', 'Type1', 'Type2', 'Type3', 'Type4', 'Type5', 'Type6', 'Type7', 'Type8', 'Type0']

print cryptoconcurrenciesName
for cryptoName in cryptoconcurrenciesName:
    file = mypath + cryptoName

    cryptoconcurrencies = rp.loadDataCSV(file, target=rp.NONE,
                                         null_target_procedure=rp.DELETE_ROW,
                                         null_procedure=rp.MEAN,
                                         na_values='-')
    df = df.append(cryptoconcurrencies.dataFrame)
    df = df.fillna(cryptoName[0:-4])

monedas = []
for i in cryptoconcurrenciesName:
    monedas.append(str(i[:-4]))

bamboo = Bamboo('Coins', df, columns, target='Market Cap')
bambooList = rp.divideDataFrame(bamboo, 'Name')

coins = []

for moneda in monedas:

    print(moneda)
    ###################
    #Caracterización
    type1 = 0
    type2 = 0
    type3 = 0
    type4 = 0
    type5 = 0
    type6 = 0
    type7 = 0
    type8 = 0
    type0 = 0
    ##################
    #Caracterización de monedas
    coin = []
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

#            print coso.dataFrame

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
                        if ltype==1:
                            type1 = type1 + 1
                        elif ltype==2:
                            type2 = type2 + 1
                        elif ltype==3:
                            type3 = type3 + 1
                        elif ltype==4:
                            type4 = type4 + 1
                        elif ltype==5:
                            type5 = type5 + 1
                        elif ltype==6:
                            type6 = type6 + 1
                        elif ltype==7:
                            type7 = type7 + 1
                        elif ltype==8:
                            type8 = type8 + 1
                        elif ltype==0:
                            type0 = type0 + 1
                        if STATE == 'P0':
                            initial_mc = vend
#                            print(initial_mc)
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
#                print "{}  a {} ".format(pd.to_datetime(au[0]), pd.to_datetime(au[1]))
                l = pd.date_range(pd.to_datetime(au[0]), pd.to_datetime(au[1]))
                

            this_ltemporal = []
#            for aux in aux_temporal:
#                ax = aux['Market Cap']
#                ax2 = aux['Date']
#                # Type 1: r (red) Type 2: g (green)
#                # Type 3: y (yellow) Type 4: k (black)
#                # Type 5: m (magenta) Type 6: c (cyan)
#                # Type 7: b (blue) Type 8: w (white)
#                for ltemporal in l_temporal:
#                    if ax2[0] == ltemporal[0] and ax2[-1] == ltemporal[1]:
#                        this_ltemporal = ltemporal
#                        break
#                typeTemp = this_ltemporal[2]
#                if typeTemp==1:
#                    ax.plot(c='r', figsize=(15, 8))
#                elif typeTemp==2:
#                    ax.plot(c='r', figsize=(15, 8))
#                elif typeTemp==3:
#                    ax.plot(c='b', figsize=(15, 8))
#                elif typeTemp==4:
#                    ax.plot(c='b', figsize=(15, 8))
#                elif typeTemp==5:
#                    ax.plot(c='r', figsize=(15, 8))
#                elif typeTemp==6:
#                    ax.plot(c='b', figsize=(15, 8))
#                elif typeTemp==7:
#                    ax.plot(c='r', figsize=(15, 8))
#                elif typeTemp==8:
#                    ax.plot(c='b', figsize=(15, 8))
#                elif typeTemp==0:
#                    ax.plot(c='y', figsize=(15, 8))
#                     
#                aux['Market Cap'] = this_ltemporal[7]
#    
#                aux['Market Cap'].plot(c='k')
                
#############################################################
                #Parte de caracterización de monedas
#['Cryptocurrency', 'Type1', 'Type2', 'Type3', 'Type4', 'Type5', 'Type6', 'Type7', 'Type8']
#############################################################
#            d_moneda = pd.DataFrame(columns=col_coins)
#            d_moneda['Cryptocurrency'] = moneda
#            d_moneda['Type1'] = type1
#            d_moneda['Type2'] = type2
#            d_moneda['Type3'] = type3
#            d_moneda['Type4'] = type4
#            d_moneda['Type5'] = type5
#            d_moneda['Type6'] = type6
#            d_moneda['Type7'] = type7
#            d_moneda['Type8'] = type8
#            d_moneda['Type0'] = type0
    coin = [moneda, type1, type2, type3, type4, type5, type6, type7, type8, type0]
    coins.append(coin)
    d_moneda = pd.DataFrame(coins,columns=['Cryptocurrency', 'Type1', 'Type2', 'Type3', 'Type4', 'Type5', 'Type6', 'Type7', 'Type8', 'Type0'])
#            dc = dc.append(d_moneda)
    
d_moneda = d_moneda.drop('Cryptocurrency', 1)
clustering(d_moneda)
                