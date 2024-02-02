import pandas as pd
import numpy as np
import pymc3 as pm
import theano.tensor as tt
import arviz as az

# Read the data
ratio = pd.read_csv("data.csv")

# Convert 'Location' to a categorical variable
ratio['Location'] = pd.Categorical(ratio['Location'])

# Initial values for the JAGS model
inits = [{'parms_lentic': [-3, 1], 'parms_lotic': [-3, 1], 'beta': [0] * 8, 'beta1': [0] * 8, 'sigma_intercept': 0.01,
          'sigma_slope': 0.01},
         {'parms_lentic': [0, 0], 'parms_lotic': [0, 0], 'beta': [0] * 8, 'beta1': [0] * 8, 'sigma_intercept': 1.2,
          'sigma_slope': 1.2},
         {'parms_lentic': [3, -1], 'parms_lotic': [3, -1], 'beta': [0] * 8, 'beta1': [0] * 8, 'sigma_intercept': 10,
          'sigma_slope': 10}]

# Data for the PyMC3 model
lamprey_data = {
    'Years': ratio['Years'].values,
    'males': ratio['Male'].values,
    'streams': pd.Categorical(ratio['Location']).codes,
    'N': len(ratio),
    'R': np.eye(2)
}

# Model specification in PyMC3
with pm.Model() as model:
    # Priors
    TAU = pm.Wishart('TAU', nu=3, V=lamprey_data['R'], shape=(2, 2))
    TAU2 = pm.Wishart('TAU2', nu=3, V=lamprey_data['R'], shape=(2, 2))
    parms_lentic = pm.MvNormal('parms_lentic', mu=np.zeros(2), tau=TAU, shape=2)
    parms_lotic = pm.MvNormal('parms_lotic', mu=np.zeros(2), tau=TAU2, shape=2)
    sigma_intercept = pm.Uniform('sigma_intercept', lower=0, upper=100)
    tau_intercept = pm.Deterministic('tau_intercept', 1 / (sigma_intercept ** 2))
    sigma_slope = pm.Uniform('sigma_slope', lower=0, upper=100)
    tau_slope = pm.Deterministic('tau_slope', 1 / (sigma_slope ** 2))

    # Regression coefficients
    beta = pm.Normal('beta', mu=parms_lentic[0], tau=tau_intercept, shape=8)
    beta1 = pm.Normal('beta1', mu=parms_lentic[1], tau=tau_slope, shape=8)

    # Likelihood
    p = pm.math.invlogit(beta[lamprey_data['streams']] + beta1[lamprey_data['streams']] * lamprey_data['Years'])
    males_obs = pm.Bernoulli('males_obs', p=p, observed=lamprey_data['males'])

    # Predictions for each stream type
    lentic = pm.Deterministic('lentic', pm.math.invlogit(parms_lentic[0] + parms_lentic[1] * (np.arange(7) - 1)))
    lotic = pm.Deterministic('lotic', pm.math.invlogit(parms_lotic[0] + parms_lotic[1] * (np.arange(7) - 1)))
    predicted = pm.Deterministic('predicted',
                                 pm.math.invlogit(beta[:8] + beta1[:8] * (np.arange(7) - 1).reshape(-1, 1)))

    # Sampling
    trace = pm.sample(2000, tune=1000, init=inits, chains=3)

# Traceplot
az.plot_trace(trace)

# Summary
summary = az.summary(trace)
print(summary)

# Highest Posterior Density (HPD) intervals
hpd = az.hpd(trace)
print(hpd)

# Posterior predictive checks for years
year_comparisons = {}
for i in range(7):
    year_comparisons[f'year{i}'] = np.mean(trace['predicted'][:, i, 0] > trace['predicted'][:, i, 1])
print(year_comparisons)


