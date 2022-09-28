import dataclasses
import pandas as pd
import numpy as np
import scipy.stats

@dataclasses.dataclass
class TestResults:
    statistic: float
    pvalue: float


def calc_sigma_sq_AR_i(eps_i, M1_i):
    """
    :param eps_i: residuals of security i
    :param M1_i: non-missing values in eps_i
    :return: sigma_sq_AR_i
    """
    return (eps_i**2).sum() / (M1_i - 2)

def calc_standardised_AR_i_t(AR_i_t, sigma_sq_AR_i, M1_i, R_market_estimation, R_market_event_day):
    """

    :param AR_i_t:  abnormal return of security i on day t
    :param sigma_sq_AR_i: variance of residuals of security i
    :param M1_i: non-missing values in eps_i
    :param R_market: market return
    :return: sigma_AR_i_t
    """
    R_market_bar = R_market_estimation.mean()
    return AR_i_t/(sigma_sq_AR_i*(1+(1/M1_i)+((R_market_event_day - R_market_bar)**2/(((R_market_estimation-R_market_bar)**2).sum()))))**(1/2)


def calc_z_BMP(standardised_ARs):
    """
    :param sigma_ARstandardised_ARs: We calculated it only for the event day so we are not slicing for the day here anymore
    :return: the unadjusted z_BMP_E
    """
    N = len(standardised_ARs)
    sigma_mean_t = standardised_ARs.mean()
    return sigma_mean_t/(1/(N*(N-1))   *  ((standardised_ARs - sigma_mean_t)**2).sum())**(1/2)

def adjust(zBMPe, eps):
    "Make adjustment to BMP test statistic"
    mean_residuals = eps.mean().mean()
    N = eps.shape[0]
    adjusted = zBMPe*((1-mean_residuals)/(1+(N-1)*mean_residuals))**(1/2)
    return adjusted

# implement an adjusted böhmer test
def adjBMP(AR, eps, M1, R_market_estimation, R_market_event_window, event_day):
    """

    :param AR: abnormal return
    :param eps: residuals of security i
    :param M1: non-missing values in eps_i
    :param R_market: market return
    :return: adjusted böhmer test
    """

    R_market_event_day = R_market_event_window[:, event_day]
    securities = AR.index
    #days = AR.columns

    sigma_sq_AR = np.asarray([calc_sigma_sq_AR_i(eps[i], M1[i]) for i in securities])
    #calc_sigma_AR = lambda i_t: calc_standardised_AR_i_t(AR[i_t[0], i_t[1]], sigma_sq_AR[i_t[0]], M1[i_t[0]], R_market_estimation[i_t[0],:], R_market_event_day[i_t[0]])
    #security_day_df = pd.DataFrame([[(m, t) for t in securities] for m in days])

    # calculate the standardised ARs for each security on the event day
    standardised_ARs_event_day = np.asarray([calc_standardised_AR_i_t(AR.iloc[i,event_day], sigma_sq_AR[i], M1[i], R_market_estimation[i,:], R_market_event_day[i]) for i in securities])
    #sigma_AR = security_day_df.applymap(calc_sigma_AR)
    # calculate
    z_BMP_E = calc_z_BMP(standardised_ARs_event_day)
    adjusted_z = adjust(z_BMP_E, eps)


    # find p-value for two-tailed test
    p = scipy.stats.norm.sf(abs(adjusted_z)) * 2
    result = TestResults(adjusted_z, p)

    return result


# implement generalised rank test
def grank():
    pass

if __name__ == "__main__":



    ### test if there are no missing values in the data, expecting high p value
    np.random.seed(3)
    AR = pd.DataFrame(np.random.standard_normal((2,5)))
    R_market_event = np.asarray([0.1, 0.1, 0.1, 0.1, 0.1])
    M1 = np.asarray(AR.shape[0]*[AR.shape[1]])

    eps = np.asarray([[0.1, 0.2, -0.3, 0.1, -0.3, 0.1], [0.1, 0.2, -0.3, 0.1, -0.3, 0.1]])
    R_market_estimation = np.asarray([[0.37, 0.23, 0.3, 0.4, 0.13, 0.14], [0.1, 0.2, 0.3, 0.2, 0.1, 0.1]])

    event_day = 2
    R_market_event_window = np.asarray([[0.2, -0.2, 0.2, -0.2, 0.0], [0.2, -0.2, 0.2, -0.2, 0.0]])# not important , just here for constr. r market event day

    test_res = adjBMP(AR, eps, M1, R_market_estimation, R_market_event_window, event_day)

    print(test_res)