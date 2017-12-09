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

from Report import Report
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor

class Bamboo:
    
    def __init__(self, name, dataFrame, features, target=None, n_nulls=None):
        self.name = name
        self.dataFrame = dataFrame
        self.features = features 
        self.target = target
        self.n_nulls = n_nulls
        self.reports = []
        self.regressor = None
        
    def reportBasicInfo(self, printOnScreen=True):
        
        featuresType = []
        featuresMin = []
        featuresMax = []
        featuresMean = []
        
        for feature in self.features:
            featuresType.append(type(self.dataFrame[feature].iloc[0]).__name__)
            featuresMin.append(self.dataFrame[feature].min())
            featuresMax.append(self.dataFrame[feature].max())
            
            if type(self.dataFrame[feature].iloc[0]).__name__ != 'str':
                featuresMean.append(self.dataFrame[feature].mean())
                
            else:
                featuresMean.append('none')
        
        name='BasicInfo'+str(self.numberOfReports('Basic')+1)
        
        report = Report(name,
                    cols=zip(self.features, featuresType, 
                    featuresMin, featuresMax, featuresMean, self.n_nulls),
                    headers=["Feature","Type","Min","Max","Mean","Num Nulls"],
                    typeReport='Basic')
        
        if printOnScreen:
            report.showReport();
        self.reports.append(report)
    
    def reportInfoRelevancies(self, printOnScreen=True):
        name = 'RelevanciesInfo'+str(self.numberOfReports('Relevancies')+1)
        report = Report(name,
                    cols = zip(self.features, self.regressor.feature_importances_),
                    headers=["Feature","Relevancy"],
                    typeReport='Relevancies')
        if printOnScreen:
            report.showReport();
        self.reports.append(report)
    
    def setupRegressor(self, 
                       criterion='mae', 
                       max_depth=0,
                       n_estimators=0,
                       n_neighbors=0,
                       random_state=0, 
                       mode='DecisionTree', 
                       weights='uniform'):
    
        if mode == 'DecisionTree':
            regressor = DecisionTreeRegressor(criterion=criterion, max_depth=max_depth, 
                                              random_state=random_state)
        if mode == 'KNN':
            regressor = KNeighborsRegressor(n_neighbors, weights=weights)
            
        if mode == 'RandomForest':
            regressor = RandomForestRegressor(n_estimators=n_estimators, max_depth = max_depth, 
                                             criterion='mae', random_state=random_state)
           
        regressor.fit(self.dataFrame[self.features], self.dataFrame[self.target])
        self.regressor = regressor
    
    def numberOfReports(self, typeReport='All'):
        count = 0
        for report in self.reports:
            if report.typeReport == typeReport or typeReport == 'All':
                count = count + 1
                
        return count 