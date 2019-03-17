import numpy as np
from math import factorial
from scipy.special import binom
from numba import jit


C = np.sqrt(2.0 * np.pi)
FACTORIAL = np.array([factorial(i) for i in range(15)])
FACTORIAL_0 = FACTORIAL[0]
NPEAKS = 11
N = np.arange(NPEAKS)[:, None]
J = np.arange(NPEAKS)[None, :]
K = np.arange(1, NPEAKS)[:, None]
FACTORIAL_J_INV = 1 / FACTORIAL[J]
BINOM = binom(N - 1, J - 1)


@jit(nopython=True)
def _normal_pdf(x, mean=0, std_deviation=1):
    u = (x - mean) / std_deviation
    return np.exp(-0.5 * u ** 2) / (C * std_deviation)


@jit(nopython=True)
def _poisson_pmf_j(mu):
    return mu ** J * np.exp(-mu) * FACTORIAL_J_INV


@jit(nopython=True)
def pedestal_signal(x, norm, eped, eped_sigma, lambda_):
    p_ped = np.exp(-lambda_)  # Poisson PMF for k = 0, mu = lambda_
    signal = norm * p_ped * _normal_pdf(x, eped, eped_sigma)
    return signal


@jit
def sipm_pe_signal(k, x, norm, eped, eped_sigma, spe, spe_sigma, lambda_, opct,
              pap, dap):
    # Obtain poisson distribution
    pj = _poisson_pmf_j(lambda_)
    pct = np.sum(pj * np.power(1-opct, J) * np.power(opct, N - J) * BINOM, 1)

    sap = spe_sigma

    papk = np.power(1 - pap, N[:, 0])
    p0ap = pct * papk
    pap1 = pct * (1-papk) * papk

    pe_sigma = np.sqrt(k * spe_sigma ** 2 + eped_sigma ** 2)
    ap_sigma = np.sqrt(k * sap ** 2 + eped_sigma ** 2)

    signal = p0ap[k] * _normal_pdf(x, eped + k * spe, pe_sigma)
    signal += pap1[k] * _normal_pdf(x, eped + k * spe * (1.0-dap), ap_sigma)
    signal *= norm

    return signal


def sipm(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_, opct,
                 pap, dap, **kwargs):
    # Obtain pedestal signal
    params = [norm, eped, eped_sigma, lambda_]
    ped_s = pedestal_signal(x, *params)

    # Obtain pe signal

    params = [norm, eped, eped_sigma, spe, spe_sigma, lambda_, opct, pap, dap]
    pe_s = sipm_pe_signal(K, x[None, :], *params).sum(0)

    signal = ped_s + pe_s

    return signal


@jit
def mapm_pe_signal(k, x, norm, eped, eped_sigma, spe, spe_sigma, lambda_):
    # Obtain poisson distribution
    p = _poisson_pmf_j(lambda_)[0]

    pe_sigma = np.sqrt(k * spe_sigma ** 2 + eped_sigma ** 2)

    signal = norm * p[k] * _normal_pdf(x, eped + k * spe, pe_sigma)

    return signal


def mapm(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_, **kwargs):
    # Obtain pedestal signal
    params = [norm, eped, eped_sigma, lambda_]
    ped_s = pedestal_signal(x, *params)

    # Obtain pe signal

    params = [norm, eped, eped_sigma, spe, spe_sigma, lambda_]
    pe_s = mapm_pe_signal(K, x[None, :], *params).sum(0)

    signal = ped_s + pe_s

    return signal
