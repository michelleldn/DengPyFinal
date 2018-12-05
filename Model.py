from Operator import Operator

class Model(object):
    def __init__(self, eR, var, cov):
        '''
        :param eR: expected Return on certain time point
        :param var: variance
        :param cov: covariance matrix
        '''
        self.eR = eR
        self.var = var
        self.cov = cov

    def tenFactorModel(self):
        '''
        ten factor model by Joyce
        :return: preditcted return or CTEF
        '''
        return 0

    def selfDesignModel(self):
        '''
        self design model by Yixin
        :param predX: preditcted return or CTEF
        :return: preditcted return or CTEF
        '''
        return 0

    def meanVarModel(self, predX):
        '''
        :param predX: preditcted return or CTEF
        :return: weight matrix (dateframe, index = stock ticker, columns = weight)
        '''
        return 0


