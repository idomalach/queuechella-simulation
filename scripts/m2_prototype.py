"""M2 prototype v2: FG/Gamma + MS/Normal. Chi-square with k in [10, 15]."""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import digamma, polygamma

XLSX = "/Users/idomalach/Documents/Claude/Projects/Simulation_Project/samples_for_simulation.xlsx"


def empirical_cdf(data):
    s = np.sort(data)
    n = len(s)
    return s, np.arange(1, n + 1) / n


def ks_d(data, cdf_func):
    s, ecdf = empirical_cdf(data)
    n = len(s)
    tcdf = cdf_func(s)
    d_plus = np.max(ecdf - tcdf)
    d_minus = np.max(tcdf - (np.arange(0, n) / n))
    return max(d_plus, d_minus)


def gamma_mle(data, tol=1e-10, max_iter=200):
    """MLE for Gamma(shape=alpha, scale=beta).

    Closed form: beta_hat = x_bar / alpha_hat.
    Alpha solves: ln(alpha) - psi(alpha) = ln(x_bar) - (1/n) sum ln(x_i)
    Solve by Newton-Raphson: f(alpha) = ln(alpha) - psi(alpha) - s = 0,
    f'(alpha) = 1/alpha - psi'(alpha)
    """
    n = len(data)
    x_bar = data.mean()
    s = np.log(x_bar) - np.log(data).mean()
    # MoM initial guess for alpha
    alpha = (x_bar ** 2) / data.var(ddof=0)
    for _ in range(max_iter):
        f = np.log(alpha) - digamma(alpha) - s
        fp = 1 / alpha - polygamma(1, alpha)
        new_alpha = alpha - f / fp
        if abs(new_alpha - alpha) < tol:
            alpha = new_alpha
            break
        alpha = new_alpha
    beta = x_bar / alpha
    return alpha, beta


def chi_square_eq_prob(data, inv_cdf, n_params, k, alpha_sig=0.05):
    n = len(data)
    edges = [inv_cdf(i / k) for i in range(1, k)]
    edges = [-np.inf] + list(edges) + [np.inf]
    observed, _ = np.histogram(data, bins=edges)
    expected = np.full(k, n / k)
    chi2_stat = float(np.sum((observed - expected) ** 2 / expected))
    df = k - 1 - n_params
    crit = float(stats.chi2.ppf(1 - alpha_sig, df))
    p = float(1 - stats.chi2.cdf(chi2_stat, df))
    return chi2_stat, crit, df, p, observed.tolist(), expected.tolist()


def main():
    fg = pd.read_excel(XLSX, sheet_name="FriendsGroup_arrival_intervals")["minutes"].values
    ms = pd.read_excel(XLSX, sheet_name="MainStage_concert_duration")["minutes"].values
    n_fg, n_ms = len(fg), len(ms)

    print("=== FG / Gamma fit ===")
    a, b = gamma_mle(fg)
    print(f"MLE: shape (alpha) = {a:.6f}, scale (beta) = {b:.6f}")
    print(f"     mean=alpha*beta={a*b:.4f}  sample mean={fg.mean():.4f}")
    print(f"     var=alpha*beta^2={a*b*b:.4f}  sample var={fg.var(ddof=0):.4f}")
    print(f"scipy.gamma.fit (compare): {stats.gamma.fit(fg, floc=0)}")

    g_cdf = lambda x: stats.gamma.cdf(x, a, scale=b)
    g_inv = lambda q: stats.gamma.ppf(q, a, scale=b)

    d = ks_d(fg, g_cdf)
    crit_unmod = 1.358 / np.sqrt(n_fg)
    print(f"KS unmodified: D={d:.5f}  crit_0.05={crit_unmod:.5f}  -> {'PASS' if d < crit_unmod else 'REJECT'}")
    print(f"scipy.kstest:  {stats.kstest(fg, 'gamma', args=(a, 0, b))}")

    print("Chi-Square sweep k=10..15:")
    for k in range(10, 16):
        chi2, crit, df, p, obs, _ = chi_square_eq_prob(fg, g_inv, n_params=2, k=k)
        print(f"  k={k}: chi2={chi2:.3f}  crit={crit:.3f}  df={df}  p={p:.4f}  -> {'PASS' if chi2 < crit else 'REJECT'}  obs={obs}")

    print("\n=== MS / Normal fit ===")
    mu = ms.mean()
    sigma2 = float(((ms - mu) ** 2).sum() / n_ms)
    sigma = np.sqrt(sigma2)
    print(f"MLE: mu = {mu:.4f}, sigma^2 = {sigma2:.4f}, sigma = {sigma:.4f}")

    n_cdf = lambda x: stats.norm.cdf(x, loc=mu, scale=sigma)
    n_inv = lambda q: stats.norm.ppf(q, loc=mu, scale=sigma)

    d2 = ks_d(ms, n_cdf)
    crit_unmod2 = 1.358 / np.sqrt(n_ms)
    print(f"KS unmodified: D={d2:.5f}  crit_0.05={crit_unmod2:.5f}  -> {'PASS' if d2 < crit_unmod2 else 'REJECT'}")
    print(f"scipy.kstest:  {stats.kstest(ms, 'norm', args=(mu, sigma))}")

    print("Chi-Square sweep k=10..15:")
    for k in range(10, 16):
        chi2, crit, df, p, obs, _ = chi_square_eq_prob(ms, n_inv, n_params=2, k=k)
        print(f"  k={k}: chi2={chi2:.3f}  crit={crit:.3f}  df={df}  p={p:.4f}  -> {'PASS' if chi2 < crit else 'REJECT'}  obs={obs}")


if __name__ == "__main__":
    main()
