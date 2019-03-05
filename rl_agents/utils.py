import numpy as np


def constrain(x, a, b):
    return np.minimum(np.maximum(x, a), b)


def not_zero(x, eps=0.01):
    if abs(x) > eps:
        return x
    elif x > 0:
        return eps
    else:
        return -eps


def wrap_to_pi(x):
    return ((x+np.pi) % (2*np.pi)) - np.pi


def remap(v, x, y):
    return y[0] + (v-x[0])*(y[1]-y[0])/(x[1]-x[0])


def bernoulli_kullback_leibler(p, q):
    """
        Compute the Kullback-Leibler divergence of two Bernoulli distributions.

    :param p: parameter of the first Bernoulli distribution
    :param q: parameter of the second Bernoulli distribution
    :return: KL(B(p), B(q))
    """
    kl1, kl2 = 0, np.infty
    if p > 0:
        if q > 0:
            kl1 = p*np.log(p/q)

    if q < 1:
        if p < 1:
            kl2 = (1 - p) * np.log((1 - p) / (1 - q))
        else:
            kl2 = 0
    return kl1 + kl2


def d_bernoulli_kullback_leibler_dq(p, q):
    """
        Compute the partial derivative of the Kullback-Leibler divergence of two Bernoulli distributions.

        With respect to the parameter q of the second distribution.

    :param p: parameter of the first Bernoulli distribution
    :param q: parameter of the second Bernoulli distribution
    :return: dKL/dq(B(p), B(q))
    """
    return (1 - p) / (1 - q) - p/q


def hoeffding_upper_bound(_sum, count, time, c=4):
    """
        Upper Confidence Bound of the empirical mean built on the Chernoff-Hoeffding inequality.

    :param _sum: Sum of sample values
    :param count: Number of samples
    :param time: Allows to set the bound confidence level to time^(-c)
    :param c: Time exponent in the confidence level
    """
    return _sum / count + np.sqrt(c * np.log(time) / (2 * count))


def kl_upper_bound(_sum, count, time, c=2, eps=1e-2):
    """
        Upper Confidence Bound of the empirical mean built on the Kullback-Leibler divergence.

        The computation involves solving a small convex optimization problem using Newton Iteration

    :param _sum: Sum of sample values
    :param count: Number of samples
    :param time: Allows to set the bound confidence level
    :param c: Coefficient before the log(t) in the maximum divergence
    :param eps: Absolute accuracy of the Netwon Iteration
    """
    mu = _sum/count
    max_div = c*np.log(time)/count

    # Solve KL(mu, q) = max_div
    q = mu
    next_q = (1 + mu)/2
    while abs(q - next_q) > eps:
        q = next_q

        # Newton Iteration
        klq = bernoulli_kullback_leibler(mu, q) - max_div
        d_klq = d_bernoulli_kullback_leibler_dq(mu, q)
        next_q = q - klq / d_klq

        # Out of bounds: move toward the bound
        weight = 0.9
        if next_q > 1:
            next_q = weight*1 + (1 - weight)*q
        elif next_q < mu:
            next_q = weight*mu + (1 - weight)*q

    return constrain(q, 0, 1)


