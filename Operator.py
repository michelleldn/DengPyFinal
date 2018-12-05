import pandas as pd
import numpy as np
import quandl
from sklearn import preprocessing
from datetime import datetime

class Operator(object):
    def __init__(self):
        pass

    def dateList(self, startD, endD, rusRet):
        '''
        create date list for circulation
        :param startD: start date
        :param endD: endDate
        :param rusRet: russel 300 return which index is all the dates
        :return: datetimeIndex of  our circulation
        '''
        dt = rusRet.index
        startIdx = dt.get_loc(startD)[0]
        endIdx = dt.get_loc(endD)[0]
        # print(startIdx)
        returnDt = dt[startIdx:(endIdx+1)]
        return returnDt


    def standardize(self, df):
        '''
        standardize dataframe
        :return: normalized dataframe
        '''
        dfNorm = preprocessing.StandardScaler().fit_transform(df)
        dfNorm = pd.DataFrame(dfNorm, columns=df.columns, index=df.index)
        return dfNorm

    def evaluateIndicator(self, df):
        '''
        calculate information ratio and max drawdown
        :param df: a dataframe with monthly return of stocks or index(not annualized)
        :return: information Ratio
        '''
        # calculate highest information ratio
        infoR = df*12/(df*12).values.std(ddof=1)
        maxInfoR = np.array(infoR.max())[0]
        # calculate max drawdown = (max-min)/max
        maxDD = np.array((df.max() - df.min())/df.max())[0]
        return maxInfoR, maxDD


    def russel3000(self):
        '''
        get montly return data of russel3000 and calculate max information ratio and max drawdown
        :return: return of russel, max information ratio, max drawdown
        problem: index of the return should be changed
        '''
        quandl.ApiConfig.api_key = "fyQtvbQCozMUamzNnCxG"
        df = quandl.get('EOD/IWV', collapse="monthly", start_date='2002-11-01', end_date='2017-12-01')
        # calculate monthly return and fill nan with backfill method, standardize data
        ret = df.shift(1)/df - 1
        ret = ret[1:]
        ret.fillna(method='bfill')
        ret = ret[['Adj_Close']]
        ret = Operator.standardize(self, ret)
        # print(ret)
        # reset date for return
        ind = ret.index
        ind = ind.strftime("%m/%d/%Y")
        indDate = []
        for count in range(0, len(ind)):
            dt = ind[count]
            if dt[:2] == '12':
                dt = '01/01/' + dt[-4:]
            else:
                newMonth = int(dt[:2])+1
                if newMonth < 10:
                    dt = '0' + str(newMonth) + '/01/' + dt[-4:]
                else:
                    dt = str(newMonth) + '/01/' + dt[-4:]
            indDate.append(dt)
        indDate = pd.DataFrame(np.array(indDate), columns=['date'])
        indDate = pd.to_datetime(indDate['date'], format="%m/%d/%Y")
        ret.index = indDate
        ret.columns = ['idx_ret']
        # get information ratio and max drawdown
        maxInfoR, maxDD = Operator.evaluateIndicator(self, ret)
        return ret, maxInfoR, maxDD

    def selectStocks(self, mon, yr, dataSize, data, idxRet):
        '''
        :param mon: select month
        :param yr: select year
        :param dataSize: datasize we choose from market cap constrain
        :param data: rawData
        :return: dictionary contains each selected stocks data sort by date(ascending)
        '''
        df = data
        df['date'] = pd.to_datetime(df['DATE'], format="%m/%d/%Y")
        df['year'] = pd.DataFrame(df['date'].dt.year)
        df['month'] = pd.DataFrame(df['date'].dt.month)
        # df['ES'] = df['month']
        selectData = df[(df['year'] == yr) & (df['month'] == mon)]
        # select top dataSize(4000) market cap
        selectData = selectData.sort_values(by='date')
        selectData = selectData[:dataSize]
        # select Select stocks with ES values falling in the top 70-percentile among the [dataSize](4000) stocks
        selectData = selectData.sort_values(by='ES', ascending=False)
        percentCount = int(len(selectData)*0.7)
        selectData = selectData[:percentCount]
        selectTicker = np.array(selectData['TICKER']).tolist()
        # get data set of selected stocks
        selectStocksData = df[df['TICKER'].isin(selectTicker)]
        # get select stocks data in dictonary
        selectStocksDic = {}
        for ticker in selectTicker:
            tempDf = selectStocksData[selectStocksData['TICKER'] == ticker]
            tempDf = tempDf.sort_values(by='date')
            tempDf.index = tempDf['date']
            # standardize return
            if tempDf['RET'].empty == False:
                tempDf['RET'] = Operator.standardize(self, tempDf[['RET']])
                selectStocksDic[ticker] = tempDf
                selectStocksDic[ticker] = pd.merge(selectStocksDic[ticker], idxRet, left_index=True, right_index=True)
        # print(selectStocksDic)
        return selectStocksDic

    def getER_Var_Cov(self, dic, mon, yr):
        '''
        :param dic: dictionary of stock data
        :param mon: selected month
        :param yr: selected year
        :return: expected Return, variance and covariance all in forms of dataframe
        '''
        # calculate expected return and variance for each selected stock
        eR = []
        var = []
        covMat = pd.DataFrame()
        for ticker in dic:
            dt = dic[ticker]
            # get data in date range(past 24 months)
            indElement = dt[(dt['year']==yr) & (dt['month'] == mon)].index.tolist()[0]
            dtInd = dt.index.tolist()
            pos = dtInd.index(indElement)
            dt = dt[(pos-23):(pos+1)]
            alpha = dt['RET'] - dt['idx_ret']
            eR.append(alpha.mean())
            var.append(alpha.values.std(ddof=1))
            alpha = pd.DataFrame(np.array(alpha), columns=[ticker], index=dt.index)
            # print(alpha)
            covMat.reset_index(drop=True, inplace=True)
            alpha.reset_index(drop=True, inplace=True)
            covMat = pd.concat([covMat, alpha], axis=1)
        eR = pd.DataFrame(np.array(eR), columns=['expectedRet'], index=dic.keys())
        var = pd.DataFrame(np.array(var), columns=['Var'], index=dic.keys())
        # drop nan
        eR = eR.dropna(axis=0)
        var = var.dropna(axis=0)
        covMat = covMat.dropna(axis=1)
        # calculate covariance matrix for selected stock
        cov = covMat.cov()
        return eR, var, cov

    def calOptRet(self, weight, ret):
        '''
        get optimize weight and calculate return of the portfolio
        :param weight: optimize weight
        :param Ret:  return
        :return: portfolio return - in dataframe
        '''
        # get weighted return
        # wRet = weight*ret
        wRet = ret * ret
        sumRet = wRet.sum()
        return sumRet






