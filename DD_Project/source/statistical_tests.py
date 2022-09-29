import dataclasses
import os.path

import pandas as pd
import numpy as np
import scipy.stats

@dataclasses.dataclass
class TestResults:
    statistic: float
    pvalue: float



###################### adj-BMP TEST ############################

def calc_sigma_sq_AR_i(eps_i, M1_i):
    """
    :param eps_i: residuals of security i
    :param M1_i: non-missing values in eps_i
    :return: sigma_sq_AR_i
    """
    return (eps_i**2).sum() / (M1_i - 2)

def calc_standardised_AR_i_t(AR_i_t, sigma_sq_AR_i, M1_i, R_market_estimation_window, R_market_event_day):
    """

    :param AR_i_t:  abnormal return of security i on day t
    :param sigma_sq_AR_i: variance of residuals of security i
    :param M1_i: non-missing values in eps_i
    :param R_market: market return
    :return: sigma_AR_i_t
    """
    R_market_bar = R_market_estimation_window.mean()
    return AR_i_t/(sigma_sq_AR_i*(1+(1/M1_i)+((R_market_event_day - R_market_bar)**2/(((R_market_estimation_window-R_market_bar)**2).sum()))))**(1/2)


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
def adjBMP(AR, eps, R_market_estimation_window, R_market_event_window, event_day):
    """
    :param AR: abnormal return
    :param eps: residuals of security i
    :param M1: non-missing values in eps_i
    :param R_market: market return
    :return: adjusted böhmer test
    """

    M1 = (~np.isnan(R_market_estimation_window)).sum(axis=1)
    R_market_event_day = R_market_event_window[:, event_day]
    securities = range(AR.shape[0])

    sigma_sq_AR = np.asarray([calc_sigma_sq_AR_i(eps[i], M1[i]) for i in securities])


    # calculate the standardised ARs for each security on the event day
    standardised_ARs_event_day = np.asarray([calc_standardised_AR_i_t(AR[i,event_day], sigma_sq_AR[i], M1[i], R_market_estimation_window[i,:], R_market_event_day[i]) for i in securities])

    # calculate the unadjusted z_BMP_E
    z_BMP_E = calc_z_BMP(standardised_ARs_event_day)
    adjusted_z = adjust(z_BMP_E, eps)


    # find p-value for two-tailed test
    p = scipy.stats.norm.sf(abs(adjusted_z)) * 2 # two-tailed test, so we multiply by 2
    result = TestResults(adjusted_z, p)

    return result


###################### GRANK TEST ############################


def calculate_SCAR_star(SCAR):
    "just standardize SCAR"
    return (SCAR - SCAR.mean())/(SCAR.std(ddof=1)) # ddof=1 to get unbiased estimator of variance


def calculate_GSAR(SCAR, SAR, tau):
    "repeat SCAR tau days and concatenate arrays"
    GSAR = np.concatenate([SAR] + [SCAR.reshape(-1,1) for _ in range(tau)], axis = 1)
    return GSAR


def calculate_U(GSAR_T_script, M_T_script):
    result = (scipy.stats.rankdata(GSAR_T_script, axis=1).transpose()/(M_T_script+1)).transpose() - 0.5

    return result

def calculate_grank_Z(U, N, T_script):
    U_bar = np.asarray([1/N[t]*U[:, t].sum() for t in T_script]) # TODO ASSUMING NO NANS FOR NOW, WITH NANS WE NEED LIKE A LIST AS U
    numerator = U_bar[-1]
    denominator = U_bar.std(ddof=0) # use norming factor of 1/N and not 1/(N-1) here like in the paper
    return numerator/denominator


# implement generalised rank test
def grank(AR, eps, R_market_estimation_window, R_market_event_window, event_day):


    M1 = (~np.isnan(R_market_estimation_window)).sum(axis=1)
    L1 = R_market_estimation_window.shape[1] # TODO perhaps have to change this
    L2 = R_market_event_window.shape[1]

    R_market_event_day = R_market_event_window[:, event_day]
    securities = range(R_market_estimation_window.shape[0])
    days = range(R_market_estimation_window.shape[1])

    sigma_sq_AR = np.asarray([calc_sigma_sq_AR_i(eps[i], M1[i]) for i in securities])
    AR_estimation_and_event = np.concatenate([eps, AR], axis=1)
    calc_sigma_AR = lambda i_t: calc_standardised_AR_i_t(AR_estimation_and_event[i_t[0], i_t[1]], sigma_sq_AR[i_t[0]], M1[i_t[0]], R_market_estimation_window[i_t[0],:], R_market_event_day[i_t[0]])
    security_day_df = pd.DataFrame([[(i, t) for t in days] for i in securities])


    SAR = security_day_df.applymap(calc_sigma_AR)
    CAR = AR.sum(axis=1) #AR.cumsum(axis=1)

    factor_taking_a_lot_of_time_during_execution = (L1 + L2 + L2 / L1 + ((R_market_event_window - R_market_estimation_window.mean()) ** 2).sum() / (
            (R_market_estimation_window - R_market_estimation_window.mean()) ** 2).sum())

    def calculate_SCAR(i):

        return CAR[i] / (sigma_sq_AR[i] * factor_taking_a_lot_of_time_during_execution) ** (1 / 2)


    SCAR = np.asarray([calculate_SCAR(i) for i in securities])
    SCAR_star = calculate_SCAR_star(SCAR)
    tau = L2 # for us tau is L2
    T_script = range(0, L1+1) # for us T_script is the estimation window + 1 day from the event window
    GSAR = calculate_GSAR(SCAR_star, SAR, tau)



    N = (~np.isnan(GSAR)).sum(axis=0)
    M_T_script = (~np.isnan(GSAR[:,T_script])).sum(axis=1)
    U = calculate_U(GSAR[:,T_script], M_T_script) # TODO ASSUMING NO NANS FOR NOW, WITH NANS WE NEED LIKE A LIST AS U
    grank_Z = calculate_grank_Z(U, N, T_script)
    grank_t = grank_Z*((L1-1)/(L1  - grank_Z**2))**(1/2)
    pvalue = scipy.stats.t.sf(abs(grank_t), L1-1)*2 # two-tailed test, so we multiply by 2
    result = TestResults(grank_t, pvalue)


    return result

if __name__ == "__main__":



    ### test if there are no missing values in the data, expecting high p value
    np.random.seed(3)
    AR = np.random.standard_normal((2,5))
    R_market_event_window = np.asarray([0.1, 0.1, 0.1, 0.1, 0.1])


    eps = np.asarray([[0.1, 0.2, -0.3, 0.1, -0.3, 0.1], [0.1, 0.2, -0.3, 0.1, -0.3, 0.1]])
    R_market_estimation_window = np.asarray([[0.37, 0.23, 0.3, 0.4, 0.13, 0.14], [0.1, 0.2, 0.3, 0.2, 0.1, 0.1]])

    event_day = 2
    R_market_event_window = np.asarray([[0.2, -0.2, 0.2, -0.2, 0.0], [0.2, -0.2, 0.2, -0.2, 0.0]])# not important , just here for constr. r market event day


    test_res = adjBMP(AR, eps, R_market_estimation_window, R_market_event_window, event_day)
    print(test_res)


    test_res2 = grank(AR, eps, R_market_estimation_window, R_market_event_window, event_day)
    print(test_res2)



    ### load test pickle
    import pickle

    with open(f"../data/Niedermayer/test_params.pkl", "rb") as f:
        test_params = pickle.load(f)

    print(grank(**test_params))
