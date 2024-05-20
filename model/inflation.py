from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import numpy as np
import random

inflation_regression = None

class InflationModel:
    def __init__(self):
        self.dt = None
        self.model = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.encoder = None
        self.initInflation()
    
    def initInflation(self):
        inflation_data = pd.read_csv('datasets/us_cpi.csv', header=None)
        self.td = inflation_data
        self.td.columns = ['Date', 'CPI']
        
        self.td['CPI'] = pd.to_numeric(self.td['CPI'], errors='coerce')
        self.td = self.td.dropna(subset=['CPI'])
        
        #convert yearmon to datetime objects
        self.td['Date'] = pd.to_datetime(self.td['Date'], format='%d-%m-%Y', errors='coerce')
        self.td['Date'] = self.td['Date'] + pd.offsets.MonthEnd(0)
        self.td['Timestamp'] = (self.td['Date'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')

        #Inflation rate calculation
        self.td['Inflation Rate'] = self.td['CPI'].pct_change() * 100
        
        self.td = self.td.dropna(subset=['Inflation Rate'])

    def runLinearRegression(self, X, y):
        X = self.td['Timestamp'].values.reshape(-1,1)
        y = self.td['Inflation Rate'].values
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = LinearRegression()
        self.model.fit(self.X_train, self.y_train)
        
        self.y_pred = self.model.predict(self.X_test)
        
    def predictInflation(self, date):
        X = self.td['Timestamp'].values.reshape(-1,1)
        y = self.td['Inflation Rate'].values
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = LinearRegression()
        self.model.fit(self.X_train, self.y_train)
        future_date = pd.to_datetime(date["date"], format='%Y-%m-%d')
        future_timestamp = (future_date - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
        future_inflation_rate = self.model.predict(np.array([future_timestamp]).reshape(1,-1))
        
        randomInt = random.randint(1,50)
        
        if randomInt == 1:
            future_inflation_rate[0]*=2
        return future_inflation_rate[0]*10
def initInflation():
    global inflation_regression
    inflation_regression = InflationModel()
    inflation_regression.initInflation()
    X = inflation_regression.td['Timestamp']
    y = inflation_regression.td['Inflation Rate']
    inflation_regression.runLinearRegression(X, y)