import scipy as sp
import numpy as np

def average(elements: list) -> float:
    """
    Returns the arithmetic mean of a list of numbers.

    Args:
        elements: List of numeric values to average.

    Returns:
        The arithmetic mean of the elements.
    """
    return sum(elements) / len(elements)

def average_if(elements: list, condition: callable) -> float:
    """
    Returns the average of elements that satisfy a given condition.

    Args:
        elements:  List of numeric values to filter and average.
        condition: A callable that takes a single element and returns True
                   if it should be included in the average.

    Returns:
        The arithmetic mean of the filtered elements.
    """
    filtered_elements = [element for element in elements if condition(element)]
    return average(filtered_elements)

def average_ifs(elements: list, conditions: list) -> float:
    """
    Returns the average of elements that satisfy all given conditions simultaneously.

    Args:
        elements:   List of numeric values to filter and average.
        conditions: List of callables, each taking a single element and returning
                    True if that condition is met. Only elements passing all
                    conditions are included.

    Returns:
        The arithmetic mean of the filtered elements.
    """
    filtered_elements = [element for element in elements if all(condition(element) for condition in conditions)]
    return average(filtered_elements)

def beta (alpha: float, beta: float) -> float:
    """
    Returns the value of Euler's Beta function B(alpha, beta).

    The Beta function is defined as B(a, b) = Γ(a)·Γ(b) / Γ(a+b), where Γ
    is the Gamma function. It appears frequently in probability distributions
    and combinatorics.

    Args:
        alpha: First shape parameter (must be positive).
        beta:  Second shape parameter (must be positive).

    Returns:
        The value of B(alpha, beta).
    """
    return sp.special.beta(alpha, beta)

def beta_dist (alpha: float, beta: float, value:float, inf_limit: float =0, sup_limit: float = 100) -> float:
    """
    Returns the probability density (PDF) of the Beta distribution at a given value.

    The Beta distribution is defined on a bounded interval [inf_limit, sup_limit]
    and is controlled by two shape parameters. It is commonly used to model
    proportions, probabilities, or any variable constrained to a fixed range.

    Args:
        alpha:     First shape parameter (controls left-skew when alpha > 1).
        beta:      Second shape parameter (controls right-skew when beta > 1).
        value:     The point at which to evaluate the density. Must be within
                   [inf_limit, sup_limit].
        inf_limit: Lower bound of the distribution's support (default 0).
        sup_limit: Upper bound of the distribution's support (default 100).

    Returns:
        The PDF value at the given point.
    """
    if value < inf_limit or value > sup_limit:
        raise ValueError("Value must be between inf_limit and sup_limit.")
    return sp.stats.beta.pdf(value, alpha, beta, loc=inf_limit, scale=sup_limit - inf_limit)

def beta_dist_accumulative (alpha: float, beta: float, value:float, inf_limit: float =0, sup_limit: float = 100) -> float:
    """
    Returns the cumulative probability (CDF) of the Beta distribution up to a given value.

    Computes P(X ≤ value) for a Beta-distributed variable X on [inf_limit, sup_limit].

    Args:
        alpha:     First shape parameter (controls left-skew when alpha > 1).
        beta:      Second shape parameter (controls right-skew when beta > 1).
        value:     The point up to which to accumulate probability. Must be within
                   [inf_limit, sup_limit].
        inf_limit: Lower bound of the distribution's support (default 0).
        sup_limit: Upper bound of the distribution's support (default 100).

    Returns:
        The cumulative probability P(X ≤ value).
    """
    if value < inf_limit or value > sup_limit:
        raise ValueError("Value must be between inf_limit and sup_limit.")
    return sp.stats.beta.cdf(value, alpha, beta, loc=inf_limit, scale=sup_limit - inf_limit)

def beta_dist_inv (alpha: float, beta: float, value:float, inf_limit: float =0, sup_limit: float = 100) -> float:
    """
    Returns the inverse CDF (quantile function) of the Beta distribution.

    Finds the point x such that P(X ≤ x) = value. Useful for computing
    critical values or credible intervals.

    Args:
        alpha:     First shape parameter (controls left-skew when alpha > 1).
        beta:      Second shape parameter (controls right-skew when beta > 1).
        value:     Cumulative probability to invert. Must be in [0, 1].
        inf_limit: Lower bound of the distribution's support (default 0).
        sup_limit: Upper bound of the distribution's support (default 100).

    Returns:
        The quantile x such that P(X ≤ x) = value.
    """
    if value < 0 or value > 1:
        raise ValueError("Value must be between 0 and 1.")
    return sp.stats.beta.ppf(value, alpha, beta, loc=inf_limit, scale=sup_limit - inf_limit)

def binomial_dist (n: int, p: float, value: int) -> float:
    """
    Returns the probability mass (PMF) of the Binomial distribution at a given value.

    Computes P(X = value) for a Binomial random variable X representing the
    number of successes in n independent Bernoulli trials.

    Args:
        n:     Total number of independent trials.
        p:     Probability of success on each individual trial (must be in [0, 1]).
        value: Number of successes at which to evaluate the PMF (must be in [0, n]).

    Returns:
        The probability of observing exactly `value` successes.
    """
    if value < 0 or value > n:
        raise ValueError("Value must be between 0 and n.")
    return sp.stats.binom.pmf(value, n, p)

def binomial_dist_accumulative (n: int, p: float, value: int) -> float:
    """
    Returns the cumulative probability (CDF) of the Binomial distribution up to a given value.

    Computes P(X ≤ value) for a Binomial random variable X representing the
    number of successes in n independent Bernoulli trials.

    Args:
        n:     Total number of independent trials.
        p:     Probability of success on each individual trial (must be in [0, 1]).
        value: Maximum number of successes. Must be in [0, n].

    Returns:
        The cumulative probability P(X ≤ value).
    """
    if value < 0 or value > n:
        raise ValueError("Value must be between 0 and n.")
    return sp.stats.binom.cdf(value, n, p)

def binomial_dist_inv (n: int, p: float, value: float) -> int:
    """
    Returns the inverse CDF (quantile function) of the Binomial distribution.

    Finds the smallest integer k such that P(X ≤ k) ≥ value.

    Args:
        n:     Total number of independent trials.
        p:     Probability of success on each individual trial (must be in [0, 1]).
        value: Cumulative probability to invert. Must be in [0, 1].

    Returns:
        The smallest integer k satisfying P(X ≤ k) ≥ value.
    """
    if value < 0 or value > 1:
        raise ValueError("Value must be between 0 and 1.")
    return sp.stats.binom.ppf(value, n, p)

def binomial_dist_range (n: int, p: float, inf_value: int, sup_value: int) -> float:
    """
    Returns the probability that a Binomial variable falls within a given range.

    Computes P(inf_value ≤ X ≤ sup_value) for a Binomial random variable X.

    Args:
        n:         Total number of independent trials.
        p:         Probability of success on each individual trial (must be in [0, 1]).
        inf_value: Lower bound of the range (inclusive). Must be ≥ 0.
        sup_value: Upper bound of the range (inclusive). Must be ≤ n.

    Returns:
        The probability P(inf_value ≤ X ≤ sup_value).
    """
    if inf_value < 0 or sup_value > n:
        raise ValueError("Values must be between 0 and n.")
    if inf_value > sup_value:
        raise ValueError("inf_value must be less than or equal to sup_value.")
    return sp.stats.binom.cdf(sup_value, n, p) - sp.stats.binom.cdf(inf_value - 1, n, p)

def chi_squared_dist (df: int, value: float) -> float:
    """
    Returns the probability density (PDF) of the Chi-Squared distribution at a given value.

    The Chi-Squared distribution arises when summing the squares of df independent
    standard normal variables. It is widely used in goodness-of-fit and independence tests.

    Args:
        df:    Degrees of freedom, representing the number of independent squared
               normal variables summed (must be a positive integer).
        value: The point at which to evaluate the density (must be ≥ 0).

    Returns:
        The PDF value at the given point.
    """
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0.")
    return sp.stats.chi2.pdf(value, df)

def chi_squared_dist_accumulative (df: int, value: float) -> float:
    """
    Returns the cumulative probability (CDF) of the Chi-Squared distribution up to a given value.

    Computes P(X ≤ value) for a Chi-Squared variable with the specified degrees of freedom.

    Args:
        df:    Degrees of freedom, representing the number of independent squared
               normal variables summed (must be a positive integer).
        value: The point up to which to accumulate probability (must be ≥ 0).

    Returns:
        The cumulative probability P(X ≤ value).
    """
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0.")
    return sp.stats.chi2.cdf(value, df)

def chi_squared_dist_inv (df: int, value: float) -> float:
    """
    Returns the inverse CDF (quantile function) of the Chi-Squared distribution.

    Finds the critical value x such that P(X ≤ x) = value. Commonly used to
    determine rejection regions in hypothesis tests.

    Args:
        df:    Degrees of freedom, representing the number of independent squared
               normal variables summed (must be a positive integer).
        value: Cumulative probability to invert. Must be in [0, 1].

    Returns:
        The critical value x such that P(X ≤ x) = value.
    """
    if value < 0 or value > 1:
        raise ValueError("Value must be between 0 and 1.")
    return sp.stats.chi2.ppf(value, df)

def chi_squared_dist_p_value (df: int, value: float) -> float:
    """
    Returns the p-value from a Chi-Squared distribution for a given test statistic.

    Computes P(X > value), i.e. the probability of observing a test statistic
    at least as extreme as `value` under the null hypothesis.

    Args:
        df:    Degrees of freedom, representing the number of independent squared
               normal variables summed (must be a positive integer).
        value: The observed Chi-Squared test statistic (must be ≥ 0).

    Returns:
        The p-value P(X > value).
    """
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0.")
    return 1 - sp.stats.chi2.cdf(value, df)

def confidence_interval_normal (data: list, confidence: float = 0.95) -> tuple:
    """
    Returns the confidence interval for the population mean assuming a normal distribution.

    Uses the t-distribution internally to account for sample size, making it
    appropriate for small samples as well as large ones.

    Args:
        data:       List of observed numeric values from the sample.
        confidence: Desired confidence level as a proportion, e.g. 0.95 for 95%
                    (must be in [0, 1], default 0.95).

    Returns:
        A tuple (lower_bound, upper_bound) representing the confidence interval.
    """
    if confidence < 0 or confidence > 1:
        raise ValueError("Confidence must be between 0 and 1.")
    mean = np.mean(data)
    sem = sp.stats.sem(data)
    margin_of_error = sem * sp.stats.t.ppf((1 + confidence) / 2, len(data) - 1)
    return (mean - margin_of_error, mean + margin_of_error)

def confidence_interval_student (data: list, confidence: float = 0.95) -> tuple:
    """
    Returns the confidence interval for the population mean using the Student's t-distribution.

    Appropriate when the population standard deviation is unknown and the sample
    size is small. Uses the t critical value corresponding to the given confidence level.

    Args:
        data:       List of observed numeric values from the sample.
        confidence: Desired confidence level as a proportion, e.g. 0.95 for 95%
                    (must be in [0, 1], default 0.95).

    Returns:
        A tuple (lower_bound, upper_bound) representing the confidence interval.
    """
    if confidence < 0 or confidence > 1:
        raise ValueError("Confidence must be between 0 and 1.")
    mean = np.mean(data)
    sem = sp.stats.sem(data)
    margin_of_error = sem * sp.stats.t.ppf((1 + confidence) / 2, len(data) - 1)
    return (mean - margin_of_error, mean + margin_of_error)

def correlation (x: list, y: list) -> float:
    """
    Returns the Pearson correlation coefficient between two variables.

    Measures the strength and direction of the linear relationship between x and y.
    A value of +1 indicates perfect positive correlation, -1 perfect negative
    correlation, and 0 no linear correlation.

    Args:
        x: List of observed values for the first variable.
        y: List of observed values for the second variable. Must be the same
           length as x.

    Returns:
        The Pearson correlation coefficient, in the range [-1, 1].
    """
    if len(x) != len(y):
        raise ValueError("Lists must have the same length.")
    return np.corrcoef(x, y)[0][1]

def covariance (x: list, y: list) -> float:
    """
    Returns the sample covariance between two variables.

    Covariance measures how two variables change together. A positive value
    indicates they tend to increase together; a negative value indicates one
    tends to decrease as the other increases.

    Args:
        x: List of observed values for the first variable.
        y: List of observed values for the second variable. Must be the same
           length as x.

    Returns:
        The sample covariance between x and y.
    """
    if len(x) != len(y):
        raise ValueError("Lists must have the same length.")
    return np.cov(x, y)[0][1]

def desviation (data: list) -> float:
    """
    Returns the sample standard deviation of a dataset.

    Uses Bessel's correction (ddof=1), dividing by n-1 to produce an unbiased
    estimate of the population standard deviation from a sample.

    Args:
        data: List of numeric observations from the sample.

    Returns:
        The sample standard deviation.
    """
    return np.std(data, ddof=1)

def desviation_population (data: list) -> float:
    """
    Returns the population standard deviation of a dataset.

    Divides by n (ddof=0), appropriate when the data represents the entire
    population rather than a sample.

    Args:
        data: List of numeric values representing the full population.

    Returns:
        The population standard deviation.
    """
    return np.std(data, ddof=0)

def desviation_sample (data: list) -> float:
    """
    Returns the sample standard deviation of a dataset.

    Uses Bessel's correction (ddof=1), dividing by n-1 to produce an unbiased
    estimate of the population standard deviation from a sample.

    Args:
        data: List of numeric observations from the sample.

    Returns:
        The sample standard deviation.
    """
    return np.std(data, ddof=1)

def mean (data: list) -> float:
    """
    Returns the arithmetic mean (average) of a dataset.

    Args:
        data: List of numeric values.

    Returns:
        The arithmetic mean of the data.
    """
    return np.mean(data)

def geometric_mean (data: list) -> float:
    """
    Returns the geometric mean of a dataset.

    The geometric mean is the n-th root of the product of all values. It is
    appropriate for data that is multiplicative or spans several orders of
    magnitude, such as growth rates or financial returns.

    Args:
        data: List of positive numeric values.

    Returns:
        The geometric mean of the data.
    """
    return sp.stats.gmean(data)

def harmonic_mean (data: list) -> float:
    """
    Returns the harmonic mean of a dataset.

    The harmonic mean is the reciprocal of the arithmetic mean of reciprocals.
    It is most appropriate for rates and ratios, such as speeds or price-to-earnings
    ratios, where averaging reciprocals is meaningful.

    Args:
        data: List of positive numeric values.

    Returns:
        The harmonic mean of the data.
    """
    return sp.stats.hmean(data)

def median (data: list) -> float:
    """
    Returns the median (middle value) of a dataset.

    The median is the value that separates the lower half from the upper half
    of the data when sorted. It is robust to outliers, unlike the arithmetic mean.

    Args:
        data: List of numeric values.

    Returns:
        The median of the data.
    """
    return np.median(data)

def mode (data: list) -> float:
    """
    Returns the mode (most frequently occurring value) of a dataset.

    If multiple values share the highest frequency, returns the smallest one.

    Args:
        data: List of numeric values.

    Returns:
        The most frequently occurring value in the data.
    """
    return sp.stats.mode(data).mode

def exp_dist (lambda_: float, value: float) -> float:
    """
    Returns the probability density (PDF) of the Exponential distribution at a given value.

    The Exponential distribution models the time between events in a Poisson process,
    where events occur continuously and independently at a constant average rate.

    Args:
        lambda_: Rate parameter (average number of events per unit of time or space).
                 The mean of the distribution equals 1 / lambda_.
        value:   The point at which to evaluate the density (must be ≥ 0).

    Returns:
        The PDF value at the given point.
    """
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0.")
    return sp.stats.expon.pdf(value, scale=1/lambda_)

def exp_dist_accumulative (lambda_: float, value: float) -> float:
    """
    Returns the cumulative probability (CDF) of the Exponential distribution up to a given value.

    Computes P(X ≤ value), i.e. the probability that the waiting time until the
    next event is at most `value`.

    Args:
        lambda_: Rate parameter (average number of events per unit of time or space).
                 The mean of the distribution equals 1 / lambda_.
        value:   The point up to which to accumulate probability (must be ≥ 0).

    Returns:
        The cumulative probability P(X ≤ value).
    """
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0.")
    return sp.stats.expon.cdf(value, scale=1/lambda_)

def exp_dist_inv (lambda_: float, value: float) -> float:
    """
    Returns the inverse CDF (quantile function) of the Exponential distribution.

    Finds the time t such that P(X ≤ t) = value, i.e. the waiting time that is
    not exceeded with probability `value`.

    Args:
        lambda_: Rate parameter (average number of events per unit of time or space).
                 The mean of the distribution equals 1 / lambda_.
        value:   Cumulative probability to invert. Must be in [0, 1].

    Returns:
        The quantile t such that P(X ≤ t) = value.
    """
    if value < 0 or value > 1:
        raise ValueError("Value must be between 0 and 1.")
    return sp.stats.expon.ppf(value, scale=1/lambda_)

def f_dist (dfn: int, dfd: int, value: float) -> float:
    """
    Returns the probability density (PDF) of the F distribution at a given value.

    The F distribution is the ratio of two independent Chi-Squared variables divided
    by their respective degrees of freedom. It is central to ANOVA and regression
    significance tests.

    Args:
        dfn:   Degrees of freedom of the numerator (number of groups minus one
               in ANOVA, or number of predictors in regression).
        dfd:   Degrees of freedom of the denominator (total observations minus
               number of groups, or residual degrees of freedom).
        value: The point at which to evaluate the density (must be ≥ 0).

    Returns:
        The PDF value at the given point.
    """
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0.")
    return sp.stats.f.pdf(value, dfn, dfd)

def f_dist_accumulative (dfn: int, dfd: int, value: float) -> float:
    """
    Returns the cumulative probability (CDF) of the F distribution up to a given value.

    Computes P(X ≤ value) for an F-distributed variable with the given degrees of freedom.

    Args:
        dfn:   Degrees of freedom of the numerator (number of groups minus one
               in ANOVA, or number of predictors in regression).
        dfd:   Degrees of freedom of the denominator (total observations minus
               number of groups, or residual degrees of freedom).
        value: The point up to which to accumulate probability (must be ≥ 0).

    Returns:
        The cumulative probability P(X ≤ value).
    """
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0.")
    return sp.stats.f.cdf(value, dfn, dfd)

def f_dist_inv (dfn: int, dfd: int, value: float) -> float:
    """
    Returns the inverse CDF (quantile function) of the F distribution.

    Finds the critical value x such that P(X ≤ x) = value. Used to determine
    the rejection region in F-tests (ANOVA, regression significance).

    Args:
        dfn:   Degrees of freedom of the numerator (number of groups minus one
               in ANOVA, or number of predictors in regression).
        dfd:   Degrees of freedom of the denominator (total observations minus
               number of groups, or residual degrees of freedom).
        value: Cumulative probability to invert. Must be in [0, 1].

    Returns:
        The critical value x such that P(X ≤ x) = value.
    """
    if value < 0 or value > 1:
        raise ValueError("Value must be between 0 and 1.")
    return sp.stats.f.ppf(value, dfn, dfd)

def forecast (data: list, steps: int) -> list:
    """
    Returns future values forecasted by fitting a linear trend to the data.

    Fits a simple linear regression (OLS) to the data using its index as the
    independent variable, then extrapolates the fitted line beyond the last
    observed point.

    Args:
        data:  List of observed numeric values in chronological order.
        steps: Number of future time steps to forecast beyond the last observation.

    Returns:
        A list of `steps` forecasted values.
    """
    model = sp.stats.linregress(range(len(data)), data)
    slope, intercept = model.slope, model.intercept
    return [intercept + slope * (len(data) + i) for i in range(steps)]

def gamma (alpha: float) -> float:
    """
    Returns the value of the Gamma function Γ(alpha).

    The Gamma function generalises the factorial to real and complex numbers:
    Γ(n) = (n-1)! for positive integers. It appears in many probability
    distributions such as the Gamma, Beta, and Chi-Squared distributions.

    Args:
        alpha: The argument of the Gamma function (must be positive for real output).

    Returns:
        The value of Γ(alpha).
    """
    return sp.special.gamma(alpha)

def gamma_dist (alpha: float, beta: float, value: float) -> float:
    """
    Returns the probability density (PDF) of the Gamma distribution at a given value.

    The Gamma distribution models the waiting time until the alpha-th event in a
    Poisson process with rate 1/beta. It is also used to model skewed, positive
    continuous variables such as insurance claims or rainfall amounts.

    Args:
        alpha: Shape parameter (number of events to wait for; must be positive).
               Higher values shift the distribution rightward and make it more
               symmetric.
        beta:  Scale parameter (average time between individual events; must be
               positive). Equal to 1/lambda where lambda is the event rate.
        value: The point at which to evaluate the density (must be ≥ 0).

    Returns:
        The PDF value at the given point.
    """
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0.")
    return sp.stats.gamma.pdf(value, alpha, scale=beta)

def gamma_dist_accumulative (alpha: float, beta: float, value: float) -> float:
    """
    Returns the cumulative probability (CDF) of the Gamma distribution up to a given value.

    Computes P(X ≤ value) for a Gamma-distributed waiting time.

    Args:
        alpha: Shape parameter (number of events to wait for; must be positive).
        beta:  Scale parameter (average time between individual events; must be positive).
        value: The point up to which to accumulate probability (must be ≥ 0).

    Returns:
        The cumulative probability P(X ≤ value).
    """
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0.")
    return sp.stats.gamma.cdf(value, alpha, scale=beta)

def gamma_dist_inv (alpha: float, beta: float, value: float) -> float:
    """
    Returns the inverse CDF (quantile function) of the Gamma distribution.

    Finds the value x such that P(X ≤ x) = value.

    Args:
        alpha: Shape parameter (number of events to wait for; must be positive).
        beta:  Scale parameter (average time between individual events; must be positive).
        value: Cumulative probability to invert. Must be in [0, 1].

    Returns:
        The quantile x such that P(X ≤ x) = value.
    """
    if value < 0 or value > 1:
        raise ValueError("Value must be between 0 and 1.")
    return sp.stats.gamma.ppf(value, alpha, scale=beta)

def lognormal_dist (mu: float, sigma: float, value: float) -> float:
    """
    Returns the probability density (PDF) of the Log-Normal distribution at a given value.

    A variable follows a Log-Normal distribution if its natural logarithm is normally
    distributed. It is commonly used to model strictly positive quantities such as
    asset prices, incomes, or biological measurements.

    Args:
        mu:    Mean of the underlying normal distribution (i.e. the expected value
               of ln(X)).
        sigma: Standard deviation of the underlying normal distribution (i.e. the
               std dev of ln(X)). Must be positive.
        value: The point at which to evaluate the density (must be ≥ 0).

    Returns:
        The PDF value at the given point.
    """
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0.")
    return sp.stats.lognorm.pdf(value, s=sigma, scale=np.exp(mu))

def lognormal_dist_accumulative (mu: float, sigma: float, value: float) -> float:
    """
    Returns the cumulative probability (CDF) of the Log-Normal distribution up to a given value.

    Computes P(X ≤ value) for a Log-Normally distributed variable.

    Args:
        mu:    Mean of the underlying normal distribution (i.e. the expected value
               of ln(X)).
        sigma: Standard deviation of the underlying normal distribution (i.e. the
               std dev of ln(X)). Must be positive.
        value: The point up to which to accumulate probability (must be ≥ 0).

    Returns:
        The cumulative probability P(X ≤ value).
    """
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0.")
    return sp.stats.lognorm.cdf(value, s=sigma, scale=np.exp(mu))

def lognormal_dist_inv (mu: float, sigma: float, value: float) -> float:
    """
    Returns the inverse CDF (quantile function) of the Log-Normal distribution.

    Finds the value x such that P(X ≤ x) = value.

    Args:
        mu:    Mean of the underlying normal distribution (i.e. the expected value
               of ln(X)).
        sigma: Standard deviation of the underlying normal distribution (i.e. the
               std dev of ln(X)). Must be positive.
        value: Cumulative probability to invert. Must be in [0, 1].

    Returns:
        The quantile x such that P(X ≤ x) = value.
    """
    if value < 0 or value > 1:
        raise ValueError("Value must be between 0 and 1.")
    return sp.stats.lognorm.ppf(value, s=sigma, scale=np.exp(mu))

def normal_dist (mu: float, sigma: float, value: float) -> float:
    """
    Returns the probability density (PDF) of the Normal (Gaussian) distribution at a given value.

    The Normal distribution is the classic bell-shaped curve, fully characterised
    by its mean and standard deviation. It arises naturally through the Central
    Limit Theorem and is the basis for many statistical tests.

    Args:
        mu:    Mean of the distribution (the centre of the bell curve).
        sigma: Standard deviation of the distribution (controls the spread;
               must be positive). Larger values produce a wider, flatter curve.
        value: The point at which to evaluate the density.

    Returns:
        The PDF value at the given point.
    """
    return sp.stats.norm.pdf(value, loc=mu, scale=sigma)

def normal_dist_accumulative (mu: float, sigma: float, value: float) -> float:
    """
    Returns the cumulative probability (CDF) of the Normal distribution up to a given value.

    Computes P(X ≤ value) for a normally distributed variable, i.e. the area under
    the bell curve to the left of `value`.

    Args:
        mu:    Mean of the distribution (the centre of the bell curve).
        sigma: Standard deviation of the distribution (controls the spread;
               must be positive).
        value: The point up to which to accumulate probability.

    Returns:
        The cumulative probability P(X ≤ value).
    """
    return sp.stats.norm.cdf(value, loc=mu, scale=sigma)

def normal_dist_inv (mu: float, sigma: float, value: float) -> float:
    """
    Returns the inverse CDF (quantile function) of the Normal distribution.

    Finds the value x such that P(X ≤ x) = value. Useful for computing
    critical values, z-scores, or percentile cutoffs.

    Args:
        mu:    Mean of the distribution (the centre of the bell curve).
        sigma: Standard deviation of the distribution (controls the spread;
               must be positive).
        value: Cumulative probability to invert. Must be in [0, 1].

    Returns:
        The quantile x such that P(X ≤ x) = value.
    """
    if value < 0 or value > 1:
        raise ValueError("Value must be between 0 and 1.")
    return sp.stats.norm.ppf(value, loc=mu, scale=sigma)

def pearson_correlation (x: list, y: list) -> float:
    """
    Returns the Pearson correlation coefficient between two variables.

    Measures the strength and direction of the linear relationship between x and y.
    A value of +1 indicates perfect positive correlation, -1 perfect negative
    correlation, and 0 no linear correlation.

    Args:
        x: List of observed values for the first variable.
        y: List of observed values for the second variable. Must be the same
           length as x.

    Returns:
        The Pearson correlation coefficient, in the range [-1, 1].
    """
    if len(x) != len(y):
        raise ValueError("Lists must have the same length.")
    return np.corrcoef(x, y)[0][1]

def permutation (n: int, r: int) -> int:
    """
    Returns the number of ordered arrangements (permutations) of r items chosen from n.

    Computes P(n, r) = n! / (n - r)!, which counts the number of distinct ways
    to choose and order r items from a set of n distinct items.

    Args:
        n: Total number of distinct items available (must be non-negative).
        r: Number of items to choose and arrange (must be non-negative and ≤ n).

    Returns:
        The number of permutations P(n, r).
    """
    if n < 0 or r < 0:
        raise ValueError("n and r must be non-negative.")
    if r > n:
        raise ValueError("r must be less than or equal to n.")
    return sp.special.perm(n, r)

def quartile (data: list, q: float) -> float:
    """
    Returns the q-th quantile of a dataset.

    Finds the value below which a fraction q of the observations fall.
    For example, q=0.25 returns the first quartile (Q1), q=0.5 the median,
    and q=0.75 the third quartile (Q3).

    Args:
        data: List of numeric values.
        q:    Quantile to compute, expressed as a proportion in [0, 1].

    Returns:
        The value at the q-th quantile of the data.
    """
    if q < 0 or q > 1:
        raise ValueError("q must be between 0 and 1.")
    return np.percentile(data, q * 100)

def rank (data: list) -> list:
    """
    Returns the rank of each element in a dataset.

    Assigns ranks from 1 (smallest) to n (largest), with tied values receiving
    the average of the ranks they would otherwise occupy.

    Args:
        data: List of numeric values to rank.

    Returns:
        A list of ranks corresponding to each element in data.
    """
    return sp.stats.rankdata(data)

def skewness (data: list) -> float:
    """
    Returns the sample skewness of a dataset.

    Skewness measures the asymmetry of the distribution. A value of 0 indicates
    a symmetric distribution; positive values indicate a right (positive) tail;
    negative values indicate a left (negative) tail.

    Args:
        data: List of numeric values from the sample.

    Returns:
        The sample skewness coefficient.
    """
    return sp.stats.skew(data)

def skewness_population (data: list) -> float:
    """
    Returns the population skewness of a dataset.

    Uses the adjusted Fisher-Pearson standardised moment coefficient (bias=False),
    appropriate when the data represents the entire population.

    Args:
        data: List of numeric values representing the full population.

    Returns:
        The population skewness coefficient.
    """
    return sp.stats.skew(data, bias=False)

def slope (x: list, y: list) -> float:
    """
    Returns the slope of the simple linear regression of y on x.

    The slope quantifies how much y changes on average for each one-unit
    increase in x (i.e. the rate of change).

    Args:
        x: List of values for the independent (predictor) variable.
        y: List of values for the dependent (response) variable. Must be the
           same length as x.

    Returns:
        The slope coefficient of the fitted regression line.
    """
    if len(x) != len(y):
        raise ValueError("Lists must have the same length.")
    return sp.stats.linregress(x, y).slope

def axis_intercept (x: list, y: list) -> float:
    """
    Returns the intercept of the simple linear regression of y on x.

    The intercept is the predicted value of y when x equals zero (i.e. where
    the fitted line crosses the y-axis).

    Args:
        x: List of values for the independent (predictor) variable.
        y: List of values for the dependent (response) variable. Must be the
           same length as x.

    Returns:
        The intercept of the fitted regression line.
    """
    if len(x) != len(y):
        raise ValueError("Lists must have the same length.")
    return sp.stats.linregress(x, y).intercept

def statistics_standarization (data: list) -> list:
    """
    Returns the standardised (z-scored) values of a dataset using sample standard deviation.

    Transforms each observation by subtracting the sample mean and dividing by the
    sample standard deviation (ddof=1), producing a dataset with mean 0 and
    standard deviation 1.

    Args:
        data: List of numeric values from the sample.

    Returns:
        A list of standardised values.
    """
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    return [(x - mean) / std for x in data]

def statistics_population_standarization (data: list) -> list:
    """
    Returns the standardised values of a dataset using population standard deviation.

    Transforms each observation by subtracting the mean and dividing by the
    population standard deviation (ddof=0). Appropriate when the data represents
    the entire population.

    Args:
        data: List of numeric values representing the full population.

    Returns:
        A list of standardised values.
    """
    mean = np.mean(data)
    std = np.std(data, ddof=0)
    return [(x - mean) / std for x in data]

def statistics_sample_standarization (data: list) -> list:
    """
    Returns the standardised (z-scored) values of a dataset using sample standard deviation.

    Transforms each observation by subtracting the sample mean and dividing by the
    sample standard deviation (ddof=1). Appropriate when the data is a sample drawn
    from a larger population.

    Args:
        data: List of numeric observations from the sample.

    Returns:
        A list of standardised values.
    """
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    return [(x - mean) / std for x in data]

def standard_error (data: list) -> float:
    """
    Returns the standard error of the mean for a dataset.

    The standard error estimates how much the sample mean is expected to vary
    from the true population mean. It equals the sample standard deviation
    divided by the square root of the sample size.

    Args:
        data: List of numeric observations from the sample.

    Returns:
        The standard error of the mean.
    """
    return sp.stats.sem(data)

def standard_error_population (data: list) -> float:
    """
    Returns the standard error of the mean computed using the population standard deviation.

    Divides the population standard deviation (ddof=0) by the square root of n.
    Use this when the data represents the entire population.

    Args:
        data: List of numeric values representing the full population.

    Returns:
        The population standard error of the mean.
    """
    return sp.stats.sem(data, ddof=0)

def standard_error_sample (data: list) -> float:
    """
    Returns the standard error of the mean computed using the sample standard deviation.

    Divides the sample standard deviation (ddof=1) by the square root of n.
    Use this when the data is a sample drawn from a larger population.

    Args:
        data: List of numeric observations from the sample.

    Returns:
        The sample standard error of the mean.
    """
    return sp.stats.sem(data, ddof=1)

def t_dist (df: int, value: float) -> float:
    """
    Returns the probability density (PDF) of Student's t-distribution at a given value.

    The t-distribution is symmetric and bell-shaped like the normal distribution,
    but has heavier tails that shrink as degrees of freedom increase. It is used
    when the population standard deviation is unknown and the sample is small.

    Args:
        df:    Degrees of freedom, typically n-1 where n is the sample size.
               Higher values make the distribution approach the standard normal.
        value: The point at which to evaluate the density (must be ≥ 0).

    Returns:
        The PDF value at the given point.
    """
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0.")
    return sp.stats.t.pdf(value, df)

def t_dist_accumulative (df: int, value: float) -> float:
    """
    Returns the cumulative probability (CDF) of Student's t-distribution up to a given value.

    Computes P(X ≤ value) for a t-distributed variable with the given degrees of freedom.

    Args:
        df:    Degrees of freedom, typically n-1 where n is the sample size.
        value: The point up to which to accumulate probability (must be ≥ 0).

    Returns:
        The cumulative probability P(X ≤ value).
    """
    if value < 0:
        raise ValueError("Value must be greater than or equal to 0.")
    return sp.stats.t.cdf(value, df)

def t_dist_inv (df: int, value: float) -> float:
    """
    Returns the inverse CDF (quantile function) of Student's t-distribution.

    Finds the critical value t such that P(X ≤ t) = value. Commonly used to
    determine rejection regions or confidence interval margins.

    Args:
        df:    Degrees of freedom, typically n-1 where n is the sample size.
        value: Cumulative probability to invert. Must be in [0, 1].

    Returns:
        The critical value t such that P(X ≤ t) = value.
    """
    if value < 0 or value > 1:
        raise ValueError("Value must be between 0 and 1.")
    return sp.stats.t.ppf(value, df)

def t_value (data: list) -> float:
    """
    Returns the two-tailed critical t-value for a 95% confidence interval.

    Computes the t critical value at the 97.5th percentile (alpha/2 = 0.025)
    with n-1 degrees of freedom, where n is the sample size. This is the value
    used to construct a 95% confidence interval around the sample mean.

    Args:
        data: List of numeric observations from the sample. The sample size
              determines the degrees of freedom (df = len(data) - 1).

    Returns:
        The critical t-value for a 95% two-tailed test.
    """
    return sp.stats.t.ppf(0.975, len(data) - 1)

def trend (x: list, y: list) -> tuple:
    """
    Returns the slope and intercept of the simple linear regression of y on x.

    Fits an Ordinary Least Squares (OLS) line to the data, summarising the
    linear trend as a (slope, intercept) pair.

    Args:
        x: List of values for the independent (predictor) variable.
        y: List of values for the dependent (response) variable. Must be the
           same length as x.

    Returns:
        A tuple (slope, intercept) of the fitted regression line, where slope
        is the rate of change of y per unit of x, and intercept is the predicted
        value of y when x equals zero.
    """
    if len(x) != len(y):
        raise ValueError("Lists must have the same length.")
    model = sp.stats.linregress(x, y)
    return model.slope, model.intercept

def variance (data: list) -> float:
    """
    Returns the sample variance of a dataset.

    Uses Bessel's correction (ddof=1), dividing by n-1 to produce an unbiased
    estimate of the population variance from a sample. Variance is the square
    of the standard deviation and measures the average squared deviation from the mean.

    Args:
        data: List of numeric observations from the sample.

    Returns:
        The sample variance.
    """
    return np.var(data, ddof=1)

def variance_population (data: list) -> float:
    """
    Returns the population variance of a dataset.

    Divides by n (ddof=0), appropriate when the data represents the entire
    population. Population variance is the average squared deviation from the mean.

    Args:
        data: List of numeric values representing the full population.

    Returns:
        The population variance.
    """
    return np.var(data, ddof=0)

def variance_sample (data: list) -> float:
    """
    Returns the sample variance of a dataset.

    Uses Bessel's correction (ddof=1), dividing by n-1 to produce an unbiased
    estimate of the population variance from a sample.

    Args:
        data: List of numeric observations from the sample.

    Returns:
        The sample variance.
    """
    return np.var(data, ddof=1)

def z_score (data: list, value: float) -> float:
    """
    Returns the z-score of a given value relative to a sample dataset.

    The z-score (or standard score) expresses how many sample standard deviations
    a value is away from the sample mean. A z-score of 0 means the value equals
    the mean; ±1 means one standard deviation away, and so on.

    Args:
        data:  List of numeric observations from the sample, used to compute the
               reference mean and standard deviation.
        value: The individual value to standardise.

    Returns:
        The z-score of `value` relative to the sample. Returns 0 if the standard
        deviation is zero (all values identical).
    """
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    return (value - mean) / std if std != 0 else 0

def z_score_population (data: list, value: float) -> float:
    """
    Returns the z-score of a given value relative to a population dataset.

    Computes how many population standard deviations a value is away from the
    population mean. Uses ddof=0 (no Bessel's correction), appropriate when
    the data represents the entire population.

    Args:
        data:  List of numeric values representing the full population, used to
               compute the reference mean and standard deviation.
        value: The individual value to standardise.

    Returns:
        The population z-score of `value`. Returns 0 if the standard deviation
        is zero (all values identical).
    """
    mean = np.mean(data)
    std = np.std(data, ddof=0)
    return (value - mean) / std if std != 0 else 0