import statsmodels.api as sm
from statsmodels import regression

def run(estimation_window_market_return, estimation_window_company_return):
    X = estimation_window_market_return.values
    Y = estimation_window_company_return.values

    def linreg(x, y):
        x = sm.add_constant(x)
        model = regression.linear_model.OLS(y, x).fit()

        print(model.summary())

        # Remove the constant
        x = x[:, 1]
        return model.params[0], model.params[1]

    alpha, beta = linreg(X, Y)

    print(f'alpha: {str(alpha)}')
    print(f'beta: {str(beta)}')

    return alpha, beta