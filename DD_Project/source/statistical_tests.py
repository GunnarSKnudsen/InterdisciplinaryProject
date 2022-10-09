import dataclasses
from functools import lru_cache
import pandas as pd
import numpy as np
import scipy.stats
import pickle
from source import calculate_coefficients
from scipy.stats import t
import matplotlib.pyplot as plt
from scipy.stats import norm
import logging

# set logging to debug
logging.basicConfig(level=logging.DEBUG)

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

def calc_SAR_i_t(AR_i_t, sigma_sq_AR_i, M1_i, R_market_estimation_window_centered_squared_sum, R_market_event_day_centered_squared):
    """

    :param AR_i_t:  abnormal return of security i on day t
    :param sigma_sq_AR_i: variance of residuals of security i
    :param M1_i: non-missing values in eps_i
    :param R_market: market return
    :return: sigma_AR_i_t
    """
    return AR_i_t/(sigma_sq_AR_i*(1+(1/M1_i)+(R_market_event_day_centered_squared/(R_market_estimation_window_centered_squared_sum))))**(1/2)


def calc_z_BMP(standardised_ARs):
    """
    :param sigma_ARstandardised_ARs: We calculated it only for the event day so we are not slicing for the day here anymore
    :return: the unadjusted z_BMP_E
    """
    N = len(standardised_ARs)
    sigma_mean_t = standardised_ARs.mean()
    return sigma_mean_t/(1/(N*(N-1))   *  ((standardised_ARs - sigma_mean_t)**2).sum())**(1/2)

def calculate_average_cross_correlation(eps, threshold = 5_000_000):

    """

    :param eps: estimation window residuals
    :param threshold: Where to start subsampling, subsampling will pick threshold/2 datapoints at random without replacement and without the diagonal line
    :return: average cross correlation
    """

    @lru_cache(maxsize=None) # to save half the work
    def cross_correlation(i,j):
        return np.correlate(eps[i,:], eps[j,:])

    """
    from time import time
    start = time()
    for i in range(1000):
        for j in range(1000):
            cross_correlation(1000+i,1000+j)

    print((time()-start)/1000**2)
    """
    # TODO perhaps sample 1000000 pairs and calculate the average of those and that should be a good approximation
    # TODO ebcause right now this part is super slow because of this calculation

    # permute rows of eps
    """
    x_axis = np.arange(eps.shape[0])
    n_others = np.random.shuffle(x_axis[1:])
    np.random.shuffle(x_axis[1:])
    y_axis = []
    cross_correlations = []
    for n_max in n_others:
        for x_i in x_axis: #range(len(x_axis)-1):
            cross_correlations += [cross_correlation(x_i, n) for n in range(n_max)]


        print(n_max)
        cc_array = np.asarray(cross_correlations)
        y_axis.append(cc_array.mean())
        y_std = np.asarray(y_axis).std()
        print(y_std)

        # calculate moving average of y_axis
        #y_axis = [1,2, 3]
        #y_axis = np.asarray(y_axis)
        #res = np.cumsum(y_axis)/np.arange(1, len(y_axis)+1)
        #print(res)

        plt.plot(n_others[:n_max], y_axis)
        # plot standard deviation
        plt.plot(n_others[:n_max], np.asarray(y_axis)+y_std, color='red')
        plt.plot(n_others[:n_max], np.asarray(y_axis)-y_std, color='red')
        # clear plots
        plt.show()
        
    """
    eps = eps[np.random.permutation(eps.shape[0]),:]

    N = eps.shape[0]

    if N**2 < threshold:
        return np.mean([cross_correlation(i, j) for i in range(N) for j in range(i + 1, N) if i != j])

    print("Too many securities to calculate average cross correlation, subsampling combinations...")
    # subsample tuples
    subset = set()
    len_subset = [0]
    def draw_tuple(N):
        # draw
        tuple_drawn = tuple(np.random.randint(0, N, 2))
        if tuple_drawn in subset:
            return

        if tuple_drawn[0] == tuple_drawn[1]:
            return

        subset.add(tuple_drawn)
        len_subset[0] +=1


    while len_subset[0] < threshold/2:
        draw_tuple(N)

    subset = list(subset)

    return np.mean([cross_correlation(tuple_[0], tuple_[1]) for tuple_ in subset])


def adjust(zBMPe, eps):
    "Make adjustment to BMP test statistic"
    rho_bar_hat = calculate_average_cross_correlation(eps)
    N = eps.shape[0]
    adjusted = zBMPe*((1-rho_bar_hat)/(1+(N-1)*rho_bar_hat))**(1/2)
    return adjusted

# implement an adjusted böhmer test
def adjBMP(AR, eps, R_market_estimation_window, R_market_event_window, event_day):


    M1 = (~np.isnan(R_market_estimation_window)).sum(axis=1)
    R_market_event_day = R_market_event_window[:, event_day]
    securities = range(AR.shape[0])

    sigma_sq_AR = np.asarray([calc_sigma_sq_AR_i(eps[i], M1[i]) for i in securities])


    # calculate the standardised ARs for each security on the event day
    # the following makes the calc_SAR_i_t function less readable but much faster
    R_market_bar = R_market_estimation_window.mean(axis=1)
    R_market_estimation_window_centered_squared_sum = ((R_market_estimation_window.transpose()-R_market_bar).transpose()**2).sum(axis=1)
    R_market_event_day_centered_squared = (R_market_event_day.transpose() - R_market_bar).transpose()**2
    standardised_ARs_event_day = np.asarray([calc_SAR_i_t(AR[i,event_day], sigma_sq_AR[i], M1[i], R_market_estimation_window_centered_squared_sum[i], R_market_event_day_centered_squared[i]) for i in securities])


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
    return SCAR/SCAR.std(ddof=1) # ddof=1 to get unbiased estimator of variance


def calculate_GSAR(SCAR, SAR, L1, t_1, tau):
    "repeat SCAR tau days and concatenate arrays"
    GSAR = np.concatenate([SAR[:,:L1+t_1]]+ [SCAR.reshape(-1,1) for _ in range(tau)] + [SAR[:,L1+t_1+tau:]], axis = 1)
    return GSAR



def calculate_GSAR_old(SCAR, SAR, tau):
    "repeat SCAR tau days and concatenate arrays"
    GSAR = np.concatenate([SAR]+ [SCAR.reshape(-1,1) for _ in range(tau)], axis = 1)
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
def grank_rigid(AR, eps, R_market_estimation_window, R_market_event_window, event_day, CAR_period):

    M1 = (~np.isnan(R_market_estimation_window)).sum(axis=1)
    L1 = R_market_estimation_window.shape[1] # TODO perhaps have to change this
    L2 = R_market_event_window.shape[1]

    R_market_event_day = R_market_event_window[:, event_day]
    securities = range(R_market_estimation_window.shape[0])
    days = range(R_market_estimation_window.shape[1])

    sigma_sq_AR = np.asarray([calc_sigma_sq_AR_i(eps[i], M1[i]) for i in securities])
    AR_estimation_and_event = np.concatenate([eps, AR], axis=1)


    R_market_bar = R_market_estimation_window.mean(axis=1)
    R_market_estimation_window_centered_squared_sum = ((R_market_estimation_window.transpose()-R_market_bar).transpose()**2).sum(axis=1)
    R_market_event_day_centered_squared = (R_market_event_day.transpose() - R_market_bar).transpose()**2

    logging.debug(R_market_event_day_centered_squared)

    calc_SAR = lambda i_t: calc_SAR_i_t(AR_estimation_and_event[i_t[0], i_t[1]], sigma_sq_AR[i_t[0]], M1[i_t[0]], R_market_estimation_window_centered_squared_sum[i_t[0]], R_market_event_day_centered_squared[i_t[0]])
    security_day_df = pd.DataFrame([[(i, t) for t in days] for i in securities])


    SAR = security_day_df.applymap(calc_SAR)
    tau = L2 # for us tau is L2
    CAR = AR.cumsum(axis=1)
    CAR_tau = CAR[:,L2-1]

    factor_taking_a_lot_of_time_during_execution = (L1 + L2 + L2 / L1 + ((R_market_event_window - R_market_estimation_window.mean()) ** 2).sum() / (
            (R_market_estimation_window - R_market_estimation_window.mean()) ** 2).sum())

    def calculate_SCAR(i):

        return CAR_tau[i] / (sigma_sq_AR[i] * factor_taking_a_lot_of_time_during_execution) ** (1 / 2)


    SCAR = np.asarray([calculate_SCAR(i) for i in securities])
    SCAR_star = calculate_SCAR_star(SCAR)
    T_script = range(0, L1+1) # for us T_script is the estimation window + 1 day from the event window
    GSAR = calculate_GSAR_old(SCAR_star, SAR, tau)
    logging.debug(GSAR)


    N = (~np.isnan(GSAR)).sum(axis=0)
    M_T_script = (~np.isnan(GSAR[:,T_script])).sum(axis=1)
    U = calculate_U(GSAR[:,T_script], M_T_script) # TODO ASSUMING NO NANS FOR NOW, WITH NANS WE NEED LIKE A LIST AS U
    grank_Z = calculate_grank_Z(U, N, T_script)
    grank_t = grank_Z*((L1-1)/(L1  - grank_Z**2))**(1/2)
    pvalue = scipy.stats.t.sf(abs(grank_t), L1-1)*2 # two-tailed test, so we multiply by 2
    result = TestResults(grank_t, pvalue)


    return result

# implement generalised rank test
def grank(AR, eps, R_market_estimation_window, R_market_event_window, event_day, CAR_period):

    M1 = (~np.isnan(R_market_estimation_window)).sum(axis=1)
    M2 = (~np.isnan(R_market_event_window)).sum(axis=1)
    L1 = R_market_estimation_window.shape[1] # TODO perhaps have to change this
    L2 = R_market_event_window.shape[1]

    R_market_event_day = R_market_event_window[:, event_day]
    securities = range(R_market_estimation_window.shape[0])
    days = range(L1+L2)

    sigma_sq_AR = np.asarray([calc_sigma_sq_AR_i(eps[i], M1[i]) for i in securities])

    AR_estimation_and_event = np.concatenate([eps, AR], axis=1)


    R_market_bar = R_market_estimation_window.mean(axis=1)
    R_market_estimation_window_centered_squared_sum = ((R_market_estimation_window.transpose()-R_market_bar).transpose()**2).sum(axis=1)
    R_market_event_day_centered_squared = (R_market_event_day.transpose() - R_market_bar).transpose()**2
    #logging.debug(R_market_event_day_centered_squared)

    calc_SAR = lambda i_t: calc_SAR_i_t(AR_estimation_and_event[i_t[0], i_t[1]], sigma_sq_AR[i_t[0]], M1[i_t[0]], R_market_estimation_window_centered_squared_sum[i_t[0]], R_market_event_day_centered_squared[i_t[0]])
    security_day_df = pd.DataFrame([[(i, t) for t in days] for i in securities])

    SAR = security_day_df.applymap(calc_SAR).values

    tau = CAR_period[1] - CAR_period[0] + 1
    AR_period = AR[:, CAR_period[0]:(CAR_period[-1]+1)]
    # CAR_period = AR_period.cumsum(axis=1)
    # CAR_tau = CAR_period[:,-1]
    CAR_tau = AR_period.sum(axis=1)

    #logging.debug(CAR_tau)

    factor_taking_a_lot_of_time_during_execution = (L1 + L2 + L2 / L1 + ((R_market_event_window - R_market_estimation_window.mean()) ** 2).sum() / (
            (R_market_estimation_window - R_market_estimation_window.mean()) ** 2).sum())

    def calculate_SCAR_masterthesis(i):

        return CAR_tau[i] / (sigma_sq_AR[i] * factor_taking_a_lot_of_time_during_execution) ** (1 / 2)


    def calculate_SCAR(i):
        return CAR_tau[i] / sigma_sq_AR[i]**(1/2)

    SCAR = np.asarray([calculate_SCAR(i) for i in securities])
    SCAR_star = calculate_SCAR_star(SCAR)
    T_script = list(range(0, L1)) + [L1 + CAR_period[0]] # for us T_script is the estimation window + the first day of the CAR period
    GSAR = calculate_GSAR(SCAR_star, SAR, L1, CAR_period[0], tau)
    logging.debug(GSAR)




    M_T_script = (~np.isnan(GSAR[:,T_script])).sum(axis=1)
    N_T_script = (~np.isnan(GSAR[:,T_script])).sum(axis=0) # just called N in the paper
    T_script_zero = range(len(T_script))
    U = calculate_U(GSAR[:,T_script], M_T_script) # TODO ASSUMING NO NANS FOR NOW, WITH NANS WE NEED LIKE A LIST AS U
    logging.debug(U)
    grank_Z = calculate_grank_Z(U, N_T_script, T_script_zero)
    grank_t = grank_Z*((L1-1)/(L1  - grank_Z**2))**(1/2)
    pvalue = scipy.stats.t.sf(abs(grank_t), L1-1)*2 # two-tailed test, so we multiply by 2
    result = TestResults(grank_t, pvalue)


    return result

if __name__ == "__main__":



    CAR_period = [0, 40] # including both edges

    # load test case

    with open(f"../data/Niedermayer/test_params.pkl", "rb") as f:
        test_params = pickle.load(f)
    test_params["CAR_period"] = CAR_period
    print(grank(**test_params))
    print(grank_rigid(**test_params))

    test_params["CAR_period"] = [20, 25]
    print(grank(**test_params))
    test_params["CAR_period"] = [20, 21]
    print(grank(**test_params))
    test_params["CAR_period"] = [20, 40]
    print(grank(**test_params))


    ### SIMULATION:

    ### test if there are no missing values in the data, expecting high p value
    adjBMP_results = []
    grank_results = []

    np.random.seed(3)
    J = 1000
    for j in range(J):
        print(j)
        n_securities = 100
        event_window_market_return = np.random.normal(0, 0.1,(n_securities,41))
        event_window_company_return = np.random.normal(0, 0.05, (n_securities, 41)) + event_window_market_return


        estimation_window_market_return = np.random.normal(0, 0.1, (n_securities, 100))
        estimation_window_company_return = np.random.normal(0, 0.05, (n_securities, 100)) + estimation_window_market_return

        AR_ = []
        eps_ = []
        print("calculate AR...")
        for i in range(n_securities):
            alpha, beta, eps = calculate_coefficients.run(estimation_window_market_return[i,:], estimation_window_company_return[i,:])
            ## Calculate the abnormal returns
            abnormal_return = event_window_company_return[i,:] - alpha - beta * event_window_market_return[i,:]
            AR_.append(abnormal_return)
            eps_.append(eps)

        print("Done calculating AR")
        AR = np.asarray(AR_)
        eps = np.asarray(eps_)

        event_day = 20

        test_res = adjBMP(AR, eps, estimation_window_market_return, event_window_market_return, event_day)
        print(test_res)
        adjBMP_results.append(test_res)


        test_res2 = grank(AR, eps, estimation_window_market_return, event_window_market_return, event_day, CAR_period=CAR_period)
        print(test_res2)
        grank_results.append(test_res2)

    adj_BMP_z_stat = np.asarray([res.statistic for res in adjBMP_results])
    grank_t_stat = np.asarray([res.statistic for res in grank_results])

    # histogram of the statistics
    plt.hist(adj_BMP_z_stat, bins=20, density=True)
    # add a standard normal distribution
    x = np.linspace(-5, 5, 100)
    plt.plot(x, norm.pdf(x))

    plt.show()

    plt.hist(grank_t_stat, bins=20, density=True)
    # add a student t distribution of 99 degrees of freedom
    x = np.linspace(-5, 5, 100)
    plt.plot(x, t.pdf(x, 99))

    plt.show()
