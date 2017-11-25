# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 15:53:15 2017

@author: Edu
"""

import RedPandas as rp

from os import listdir
from os.path import isfile, join
mypath = 'Top100/'
cryptoconcurrenciesName = [f for f in listdir(mypath) if isfile(join(mypath, f))]

print cryptoconcurrenciesName
for cryptoName in cryptoconcurrenciesName:
    file = mypath + cryptoName
    cryptoconcurrencies = rp.loadDataCSV(file, target='Market Cap',
                       null_target_procedure = rp.DELETE_ROW, 
                       null_procedure = rp.MEAN)
    print(' ')
    print(cryptoName)
    cryptoconcurrencies.showBasicInfo()
    