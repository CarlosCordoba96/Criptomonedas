# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 22:20:18 2017

@author: Edu

Types of reports:
        · Other as a default for unknown types
        · Basic
        
"""

from tabulate import tabulate
import datetime
class Report:
    
    def __init__(self, name, cols, headers, typeReport='Other'):
        self.name = name
        self.cols = cols
        self.headers = headers
        self.date = datetime.datetime.now()
        self.typeReport = typeReport
        
    def showReport(self):
        print self.name
        print tabulate(self.cols, self.headers)
        print 'Done in '+str(self.date)
        print " "