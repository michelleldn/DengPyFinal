from Operator import Operator
# %matplotlib inline
import numpy as np
import statsmodels.api as sm
from scipy import optimize
import pandas as pd
import time

class Model(object):
    def __init__(self, eR, var, cov, rawData):
        '''
        :param eR: expected Return on certain time point
        :param var: variance
        :param cov: covariance matrix
        :param rawData: raw data of stock universe
        :param date: current selected date
        '''
        self.eR = eR
        self.var = var
        self.cov = cov
        self.rawData = rawData

    def tenFactorModel(self, date):
        '''
        ten factor model by Joyce
        :return: preditcted return or CTEF
        '''
        def getXY(tickers, rawData, predDate):
            # get date-1 as X date
            if predDate.month == 1:
                xYr = predDate.year - 1
                xMon = 12
            else:
                xYr = predDate.year
                xMon = predDate.month - 1
            if xMon < 10:
                xDate = '0' + str(xMon) + '/01/' + str(xYr)
            else:
                xDate = str(xMon) + '/01/' + str(xYr)

            xFactor = ['TICKER', 'DATE', 'EP', 'BP', 'CP', 'SP', 'REP', 'RBP', 'RCP', 'RSP', 'CTEF', 'PM1']
            X = rawData[xFactor]
            X = X[(X['TICKER'].isin(tickers)) & (X['DATE'] == xDate)]
            xTicker = np.array(X.TICKER).tolist()
            X = X[['EP', 'BP', 'CP', 'SP', 'REP', 'RBP', 'RCP', 'RSP', 'CTEF', 'PM1']]
            X = pd.DataFrame(np.array(X), index=xTicker, columns=X.columns)

            yFactor = ['TICKER', 'DATE', 'RET']
            Y = rawData[yFactor]
            if predDate.month < 10:
                yDate = '0' + str(predDate.month) + '/01/' + str(predDate.year)
            else:
                yDate = str(predDate.month) + '/01/' + str(predDate.year)

            Y = Y[(Y['TICKER'].isin(tickers)) & (Y['DATE'] == yDate)]
            Y = Y[['RET']]
            Y = pd.DataFrame(np.array(Y), index=xTicker, columns=Y.columns)
            print(Y)
            return X, Y

        def regression(x, y):
            x['const'] = 1
            print(x, y)
            reg = sm.OLS(endog=y, exog=x, missing='drop')
            result = reg.fit()
            print(result.summary())
            return 0
        # get X Y as dataframe from raw data
        X, Y = getXY(self.eR.index, self.rawData, date)
        # regression:
        regression(X, Y)


        return 0

    def selfDesignModel(self):
        '''
        self design model by Yixin
        :param predX: preditcted return or CTEF
        :return: preditcted return or CTEF
        '''
        return 0

    def meanVarModel(self, predX, cov):
        '''
        :param predX: preditcted return or CTEF
        :param cov: covariance from part2
        :return: weight matrix (dateframe, index = stock ticker, columns = weight)
        '''
        # convert negative covariance to positive
        eigen_vals, eigen_vecs = np.linalg.eig(np.array(cov))
        if any(i < 0 for i in eigen_vals):
            cov = np.sqrt(cov*cov.T)

        # linear optimization
        c = np.array(predX.T).tolist()[0]
        print(c)



        return 0


