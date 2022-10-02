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


def fast_OLS(X,Y):
    # implement ordinary least squares in numpy

    # add a constant to the X matrix
    X = np.c_[np.ones(X.shape[0]), X]

    # calculate the coefficients
    beta = np.linalg.inv(X.T @ X) @ X.T @ Y

    # calculate the residuals
    eps = Y - X @ beta

    return beta[0], beta[1], eps

if __name__ == "__main__":

    # simulate test data for OLS
    np.random.seed(3)
    n_securities = 100
    np.random.seed(3)
    J = 1
    from time import time
    start = time()
    epses = []
    for j in range(J):
        print(j)
        n_securities = 1

        estimation_window_market_return = np.random.normal(100, 2, (n_securities, 100))
        estimation_window_company_return = np.random.normal(0, 10, (n_securities, 100)) + estimation_window_market_return

        for i in range(n_securities):
            print("security: ", i)
            alpha, beta, eps = fast_OLS(estimation_window_market_return[i,:], estimation_window_company_return[i,:])
            print(alpha, beta, eps)
            print(eps.sum())
            epses.append(eps)
    print(time() - start)
    epses = np.asarray(epses)
    print(epses.sum())