import statsmodels.api as sm
from statsmodels import regression
import logging

def run(estimation_window_market_return, estimation_window_company_return):
    '''
    Documentation not yet written
    '''
    X = estimation_window_market_return.values
    Y = estimation_window_company_return.values

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
