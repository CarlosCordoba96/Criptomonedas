# -*- coding: utf-8 -*-
"""
Created on Sun Nov 05 20:42:55 2017

@author: Edu
"""

'''
For this library you will need:
    anaconda 2.7
    
    aditionally:
        
    pandas
    tabulate
    graphviz
'''
import pandas as pd
from Bamboo import Bamboo
from Report import Report

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from scipy.stats.stats import pearsonr

from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from sklearn.cross_validation import cross_val_score

import graphviz 
from sklearn.tree import export_graphviz

from subprocess import check_call

#Install tabulate conda install -c conda-forge tabulate
from tabulate import tabulate
'''
Returns dataFrame and features in that order

name is the name of the database 'x.csv'
target is a string with the name of the target feature
'''
NONE = 0 #No action
MEAN = 1 #Put the mean of that column
ZERO = 2 #Put a zero
DELETE_ROW = 3 #Delete row

def loadDataCSV(name, 
                target=NONE, 
                null_target_procedure = NONE,
                null_procedure = NONE,
                thousands=',',
                na_values=None):
    # load data
    dataFrame = pd.read_csv(name, na_values=na_values, thousands=thousands)
    
    if target != NONE:
        
        if null_target_procedure == MEAN:
            # fill rows with no info of the target with the mean of the target
             dataFrame[target].fillna(dataFrame.mean(), inplace=True)
        if null_target_procedure == ZERO:
            # fill rows with no info of the target with zeros
            dataFrame[target].fillna(0, inplace=True)
        if null_target_procedure == DELETE_ROW: 
            # drop rows with no info about the target data
            dataFrame = dataFrame[pd.notnull(dataFrame[target])]
    
    # count nulls before replacing them
    n_nulls = dataFrame.isnull().sum()
    
    # fill nulls
    if null_procedure == MEAN:
        dataFrame.fillna(dataFrame.mean(), inplace=True)
    if null_procedure == ZERO:
        dataFrame.fillna(0, inplace=True)
        #TODO Develop dropping rows

    return Bamboo(name, dataFrame, list(dataFrame.head(0)), target, list(n_nulls))

#Returns an array with the bamboos divided by the feature selected
    #https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.groupby.html
    #https://pandas.pydata.org/pandas-docs/stable/groupby.html
def divideDataFrame(bamboo, feature):
    df = bamboo.dataFrame
    
    dataFrameList = []
    dataFrameList = [x for _, x in df.groupby(df[feature], axis=0, sort=False)]
    bambooList = []
    count = 1
    for dataFrame in dataFrameList:
        name = bamboo.name + "_div"+str(count)
        bambooDivided = Bamboo(name,dataFrame, bamboo.features, bamboo.target, bamboo.n_nulls)
        bambooList.append(bambooDivided)
        count = count + 1
        
    return bambooList
    
def correlationFeaturesTarget(bamboo):
    # NOTE: Low correlation means there's no linear relationship; 
    # it doesn't mean there's no information in the feature that predicts the target.
    corr = []

    for feature in bamboo.features:
        local_corr = pearsonr(bamboo.dataFrame[feature], bamboo.dataFrame[bamboo.target])[0]
        corr.append(local_corr)

    y_pos = np.arange(len(bamboo.features))
 
    plt.bar(y_pos, corr, align='center', alpha=0.5)
    plt.xticks(y_pos, bamboo.features, rotation='vertical')
    plt.ylabel('Correlation')
    plt.title('Correlation features vs target')

    plt.show()
    
def visualizeTree(bamboo, out_file):
    dot_data = export_graphviz(bamboo.regressor, out_file=out_file, feature_names=bamboo.features, 
                           filled=True, rounded=True)
    graph = graphviz.Source(dot_data)
    check_call(['dot','-Tpng',out_file,'-o','tree.png'])
    img = mpimg.imread('tree.png')
    plt.imshow(img)
    plt.show()

'''
Function used to check overfitting mainly
NEEDS MORE STUDY
'''
def computeMax(bamboo):
    # Compute the max 
    mae = []
    for i in range(2, 30):
        regressor = DecisionTreeRegressor(max_depth=i)
        regressor.fit(bamboo.dataFrame[bamboo.features], bamboo.dataFrame[bamboo.target])
        pred_values = regressor.predict(bamboo.dataFrame[bamboo.features])
        maev = mean_absolute_error(bamboo.dataFrame[bamboo.target],pred_values)
        mae.append(maev)

    # Plot mae   
    plt.plot(range(2,30), mae, marker='o')
    plt.xlabel('max_depth')
    plt.ylabel('mae')
    plt.show()

def computeErrorMeasure(bamboo, printGraph=True):
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(bamboo.dataFrame[bamboo.features], 
                                                    bamboo.dataFrame[bamboo.target], 
                                                    test_size=0.4)

    bamboo.regressor.fit(X_train, y_train)

    # Test
    y_pred = bamboo.regressor.predict(X_test)

    # metrics calculation 
    from sklearn.metrics import mean_absolute_error
    mae = mean_absolute_error(y_test,y_pred)
    print "Error Measure ", mae

    if printGraph:
        import matplotlib.pyplot as plt
        xx = np.stack(i for i in range(len(y_test)))
        plt.plot(xx, y_test, c='r', label='Data')
        plt.plot(xx, y_pred, c='b', label='Prediction')
        plt.axis('tight')
        plt.legend()
        plt.title("Prediction vs Data")

        plt.show()
    
'''
Function used to check the most desirable depth with a CrossValidation method
'''

def crossValidation(bamboo, mode='DecisionTree', weights='uniform',
                                                n_estimators=0,
                                                min_range=2,
                                                max_range=30,
                                                printGraph=True,
                                                criterion='mae'):
    total_scores = []

    if mode == 'DecisionTree':
            print 'Decision Tree CV test'
    
    elif mode == 'RandomForest':
            print 'Random Forest CV test with '+str(n_estimators)+' n_estimators'
            
    elif mode == 'KNN':
            print 'KNN CV test with '+weights+' weight'
            
    for i in range(min_range, max_range):
        if mode == 'DecisionTree':
            regressor = DecisionTreeRegressor(max_depth=i)
            regressor.fit(bamboo.dataFrame[bamboo.features], 
                          bamboo.dataFrame[bamboo.target])
        
        elif mode == 'RandomForest':
            regressor = RandomForestRegressor(n_estimators=n_estimators, max_depth = i, 
                                             criterion=criterion, random_state=0)
            regressor.fit(bamboo.dataFrame[bamboo.features], 
                          bamboo.dataFrame[bamboo.target])
            
        elif mode == 'KNN':
            regressor = KNeighborsRegressor(i, weights=weights)
            regressor.fit(bamboo.dataFrame[bamboo.features], 
                          bamboo.dataFrame[bamboo.target])
            
        scores = -cross_val_score(regressor, bamboo.dataFrame[bamboo.features],
            bamboo.dataFrame[bamboo.target], scoring='neg_mean_absolute_error', 
            cv=10)
        
        total_scores.append(scores.mean())

    if printGraph == True:
        plt.plot(range(min_range,max_range), total_scores, marker='o')
        plt.xlabel('max_depth')
        plt.ylabel('cv score')
        plt.legend()
        plt.show()
    
    return total_scores
'''
Function used to check a CV scatter plot of the relevancies used to create
         a decision tree to see how they fit the data
dataFrame is a panda dataFrame
features is a string list with the features of the dataFrame that are going
         to be taken into account
target is a string with the name of the target feature
relevancies is 2 dimensional array which correspond with the name of a feature
            and with the % of how relevant is it
'''
def relevantFeaturesCrossValidation(bamboo):
    
    dataFrame = bamboo.dataFrame
    features = bamboo.features
    regressor = bamboo.regressor
    target = bamboo.target
    plt.figure(figsize=(8,6))
    relevancies = zip(features, regressor.feature_importances_)
    
    for relevancy in relevancies:
        #relevancy[0] is the name of the feature
        #relevancy[1] is the relevancy of the feature
        if relevancy[1] > 0:
            #10 is the usual number of iterations for the cv
            #Here we calculate how long is going to be the prediction based on the max and minimum values of the feature
            xx = np.array([np.linspace(np.amin(dataFrame[relevancy[0]])*0.95, 
                                       np.amax(dataFrame[relevancy[0]])*1.05, 
                                       10)]).T
            
            regressor.fit(dataFrame[relevancy[0]].reshape(-1, 1), dataFrame[target])
            plt.plot(dataFrame[relevancy[0]].reshape(-1, 1), dataFrame[target], 'o', label='observation')
            plt.plot(xx, regressor.predict(xx), linewidth=4, alpha=.7, label='prediction')
            plt.xlabel(relevancy[0])
            plt.ylabel(target)
            plt.legend()
            plt.show()    