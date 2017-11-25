# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 15:54:58 2017

@author: Edu

Description:
    
Bamboo is a Pandas DataFrame wrapper used for RedPandas. In adition of having
the raw DataFrame, it also stores aditionally information.

A Bamboo object contains:
    A pandas DataFrame "dataFrame" which represents the dataset.
    
    A String list "features" that has the features that are going to be used.
    
    A String "target" which is out target feature.
    
    An int list "n_nulls" that correspond to the number of nulls that 
    a feature had initially in its dataset. It doesn't represent the current
    number of nulls in it.
    
    A Report list "reports" which contains all the analysis done.
"""
from tabulate import tabulate

class Bamboo:
    
    def __init__(self, dataFrame, features, target, n_nulls):
        self.dataFrame = dataFrame
        self.features = features 
        self.target = target
        self.n_nulls = n_nulls
        
    def showBasicInfo(self):
        
        featuresType = []
        featuresMin = []
        featuresMax = []
        featuresMean = []
        
        for feature in self.features:
            featuresType.append(type(self.dataFrame[feature][0]).__name__)
            featuresMin.append(self.dataFrame[feature].min())
            featuresMax.append(self.dataFrame[feature].max())
            
            if type(self.dataFrame[feature][0]).__name__ != 'str':
                featuresMean.append(self.dataFrame[feature].mean())
                
            else:
                featuresMean.append('none')
                    
        aux_sheet = tabulate(zip(self.features, featuresType, self.n_nulls, 
                    featuresMin, featuresMax, featuresMean), 
                    headers=["Feature","Type","Num Nulls","Min","Max","Mean"])
    
        print aux_sheet