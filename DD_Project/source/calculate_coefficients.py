import statsmodels.api as sm
from statsmodels import regression
import logging
import numpy as np

def run(estimation_window_market_return, estimation_window_company_return):
    '''
    Documentation not yet written
    '''
    if type(estimation_window_market_return) is not np.ndarray:
        X = estimation_window_market_return.values
    else:
        X = estimation_window_market_return

    if type(estimation_window_company_return) is not np.ndarray:
        Y = estimation_window_company_return.values
    else:
        Y = estimation_window_company_return

    def linreg(x, y):
        x = sm.add_constant(x)
        model = regression.linear_model.OLS(y, x).fit()

        logging.debug(model.summary())

        # Remove the constant
        x = x[:, 1]
        return model.params[0], model.params[1], model.resid

    alpha, beta, eps = linreg(X, Y)

    logging.debug(f'alpha: {str(alpha)}')
    logging.debug(f'beta: {str(beta)}')

    return alpha, beta, eps
