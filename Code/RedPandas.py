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

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from scipy.stats.stats import pearsonr

from sklearn.tree import DecisionTreeRegressor
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
                thousands=','):
    # load data
    dataFrame = pd.read_csv(name, thousands=thousands)

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
    
    #TODO Replace fake nulls
    dataFrame.replace('-', np.nan)
    
    # fill nulls
    if null_procedure == MEAN:
        dataFrame.fillna(dataFrame.mean(), inplace=True)
    if null_procedure == ZERO:
        dataFrame.fillna(0, inplace=True)
        #TODO Develop dropping rows

    return Bamboo(dataFrame, list(dataFrame.head(0)), target, list(n_nulls))
    
'''
dataFrame is a panda dataFrame
features is a string list with the features of the dataFrame that are going
         to be taken into account
target is a string with the name of the target feature
''' 

def setupDecisionTreeRegressor(dataFrame, features, target, criterion, 
                               max_depth, random_state):
    
    regressor = DecisionTreeRegressor(criterion=criterion, max_depth=max_depth, 
                                      random_state=random_state)
    
    regressor.fit(dataFrame[features], dataFrame[target])
    return regressor

def showInfoRelevancies(features, regressor):
    print tabulate(zip(features, regressor.feature_importances_),
                   headers=["Feature","Relevancy"])
    
def correlationFeaturesTarget(dataFrame, features, target):
    # NOTE: Low correlation means there's no linear relationship; 
    # it doesn't mean there's no information in the feature that predicts the target.
    corr = []

    for feature in features:
        local_corr = pearsonr(dataFrame[feature], dataFrame[target])[0]
        corr.append(local_corr)

    y_pos = np.arange(len(features))
 
    plt.bar(y_pos, corr, align='center', alpha=0.5)
    plt.xticks(y_pos, features, rotation='vertical')
    plt.ylabel('Correlation')
    plt.title('Correlation features vs target')

    plt.show()
    
def visualizeTree(regressor, features, out_file):
    dot_data = export_graphviz(regressor, out_file=out_file, feature_names=features, 
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
def computeMax(dataFrame, features, target):
    # Compute the max 
    mae = []
    for i in range(2, 30):
        regressor = DecisionTreeRegressor(max_depth=i)
        regressor.fit(dataFrame[features], dataFrame[target])
        pred_values = regressor.predict(dataFrame[features])
        maev = mean_absolute_error(dataFrame[target],pred_values)
        mae.append(maev)

    # Plot mae   
    plt.plot(range(2,30), mae, marker='o')
    plt.xlabel('max_depth')
    plt.ylabel('mae')
    plt.show()

'''
Function used to check the most desirable depth with a CrossValidation method
'''
from sklearn import neighbors

def crossValidation(dataFrame, features, target, 
                    mode='DecisionTree', weights='uniform'):
    total_scores = []

    if mode == 'DecisionTree':
            print 'Decision Tree CV test'
            
    elif mode == 'KNN':
            print 'KNN CV test with '+weights+' weight'
            
    for i in range(2, 30):
        if mode == 'DecisionTree':
            regressor = DecisionTreeRegressor(max_depth=i)
            regressor.fit(dataFrame[features], dataFrame[target])
            
        elif mode == 'KNN':
            regressor = neighbors.KNeighborsRegressor(i, weights=weights)
            regressor.fit(dataFrame[features], dataFrame[target])
            
        scores = -cross_val_score(regressor, dataFrame[features],
            dataFrame[target], scoring='neg_mean_absolute_error', cv=10)
        total_scores.append(scores.mean())

    plt.plot(range(2,30), total_scores, marker='o')
    plt.xlabel('max_depth')
    plt.ylabel('cv score')
    plt.legend()
    plt.show()    

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
def relevantFeaturesCrossValidation(dataFrame, features, regressor, target):

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