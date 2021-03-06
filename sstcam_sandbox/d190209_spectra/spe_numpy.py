from scipy.special import binom, gammaln
import numpy as np
from numba import jit


SQRT2PI = np.sqrt(2.0 * np.pi)
K = np.arange(1, 250)
KN = K[:, None]
JN = K[None, :]


@jit
def poisson(k, mu):
    return np.exp(k * np.log(mu) - mu - gammaln(k + 1))


@jit(nopython=True, fastmath=True)
def normal_pdf(x, mean=0, std_deviation=1):
    u = (x - mean) / std_deviation
    return np.exp(-0.5 * u ** 2) / (SQRT2PI * std_deviation)


@jit(fastmath=True)
def mapm_np(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_):
    # Obtain pedestal peak
    p_ped = np.exp(-lambda_)
    ped_signal = norm * p_ped * normal_pdf(x, eped, eped_sigma)

    p = poisson(K, lambda_)  # Probability to get k avalanches

    # Skip insignificant probabilities
    significant = p > 1e-5
    p_sig = p[significant]
    k_sig = K[significant]

    # Combine spread of pedestal and pe peaks
    pe_sigma = np.sqrt(k_sig * spe_sigma ** 2 + eped_sigma ** 2)

    # Evaluate probability at each value of x
    pe_signal = norm*p_sig*normal_pdf(x[:, None], eped + k_sig*spe, pe_sigma)

    return ped_signal + pe_signal.sum(1)


# @jit
def sipm_np(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_, opct, pap, dap):
    sap = spe_sigma  # Assume the sigma of afterpulses is the same

    # Obtain pedestal peak
    p_ped = np.exp(-lambda_)
    ped_signal = norm * p_ped * normal_pdf(x, eped, eped_sigma)

    pj = poisson(JN, lambda_)  # Probability to get j initial fired cells

    # Skip insignificant probabilities
    significant = pj > 1e-5
    pj_sig = pj[significant][None, :]
    jt_sig = JN[significant][None, :]
    binom_sig = binom(KN - 1, jt_sig - 1)

    # Sum the probability from the possible combinations which result in a
    # total of k fired cells to get the total probability of k fired cells
    pk = np.sum(pj_sig * np.power(1 - opct, jt_sig) *
                np.power(opct, KN - jt_sig) * binom_sig, 1)

    # Skip insignificant probabilities
    significant = pk > 1e-5
    pk_sig = pk[significant]
    k_sig = K[significant]

    # Consider probability of afterpulses
    papk = np.power(1 - pap, k_sig)
    p0ap = pk_sig * papk
    pap1 = pk_sig * (1-papk) * papk

    # Combine spread of pedestal and pe (and afterpulse) peaks
    pe_sigma = np.sqrt(k_sig * spe_sigma ** 2 + eped_sigma ** 2)
    ap_sigma = np.sqrt(k_sig * sap ** 2 + eped_sigma ** 2)

    # Evaluate probability at each value of x
    xn = x[:, None]
    pe_signal = p0ap * normal_pdf(xn, eped + k_sig * spe, pe_sigma)
    pe_signal += pap1 * normal_pdf(xn, eped + k_sig * spe * (1-dap), ap_sigma)
    pe_signal *= norm

    return ped_signal + pe_signal.sum(1)


def mapm(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_, **kwargs):
    return mapm_np(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_)


def sipm(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_, opct, pap, dap, **kwargs):
    return sipm_np(x,  norm, eped, eped_sigma, spe, spe_sigma, lambda_, opct, pap, dap)
