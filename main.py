from Operator import Operator
from Model import Model
import pandas as pd
import numpy as np

if __name__ == '__main__':
    '''
    define class:
    Operator: structure and others
    import rawData and every class contains rawData
    '''
    op = Operator()
    rawData = pd.read_csv('Total_Data5.csv', header=0, index_col=0)

    # get russel 3000 information
    russRet, russInfoR, russMDD = op.russel3000()

    startDate = '12/01/2004'
    endDate = '03/01/2005'
    dateList = op.dateList(startDate, endDate, russRet)

    setStockAmount = 10
    optRet = []
    for date in dateList:
        print(date)
        currentYr = date.year
        currentMon = date.month
        # select trading stocks
        selectStocksDic = op.selectStocks(currentMon, currentYr, setStockAmount, rawData, russRet)
        # calculate expected return/ var/ cov for current date
        # print(1)
        eR, var, cov = op.getER_Var_Cov(selectStocksDic, currentMon, currentYr)
        # print(eR)

        # initiate models and get predicted returns(CTEF)
        model = Model(eR, var, cov, rawData)
        predX = model.tenFactorModel(date)
        # predX = model.selfDesignModel()

    #     # use mean variance model to generate optimize weight of portfolio
    #     optWeight = model.meanVarModel(eR, cov)
    #
    #     # calculate optimize return
    #     optRet.append(op.calOptRet(optWeight, predX))
    #
    # optRet = pd.DataFrame(np.array(optRet), columns=['optReturn'], index=dateList)
    # # calculate information ratio and max drawdown for portfolio strategy
    # infoR, mDD = op.evaluateIndicator(optRet)
    # print('information ratio: ', infoR)
    # print('max drawdown: ', mDD)





