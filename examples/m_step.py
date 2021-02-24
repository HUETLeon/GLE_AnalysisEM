"""
===========================
M step
===========================

Inner working of the M step,  maximum likelihood estimation of the coefficients :class:`GLE_analysisEM.GLE_Estimator`
"""
import numpy as np
import pandas as pd

# from matplotlib import pyplot as plt
from GLE_analysisEM import GLE_Estimator, GLE_BasisTransform, sufficient_stats, sufficient_stats_hidden, preprocessingTraj

# from GLE_analysisEM.utils import loadTestDatas_est


# Printing options
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", -1)

# dim_x = 1
# dim_h = 1
# model = "aboba"
# force = -np.identity(dim_x)
#
basis = GLE_BasisTransform(basis_type="linear")
# generator = GLE_Estimator(verbose=1, dim_x=dim_x, dim_h=dim_h, EnforceFDT=True, force_init=force, init_params="random", model=model, random_state=42)
# X, idx, Xh = generator.sample(n_samples=1000, n_trajs=500, x0=0.0, v0=0.0, basis=basis)

dim_x = 1
dim_h = 1
random_state = 42
model = "aboba"
force = -np.identity(dim_x)

A = np.array([[5, 1.0], [-1.0, 0.5]])
C = np.identity(dim_x + dim_h)
# ------ Generation ------#
pot_gen = GLE_BasisTransform(basis_type="linear")
# pot_gen_polynom = GLE_BasisTransform(basis_type="polynomial", degree=3)
generator = GLE_Estimator(verbose=2, dim_x=dim_x, dim_h=dim_h, EnforceFDT=False, force_init=force, init_params="user", A_init=A, C_init=C, model=model, random_state=random_state)
X, idx, Xh = generator.sample(n_samples=10000, n_trajs=25, x0=0.0, v0=0.0, basis=pot_gen)

# X, idx, Xh = loadTestDatas_est(["../GLE_analysisEM/tests/0_trajectories.dat", "../GLE_analysisEM/tests/1_trajectories.dat"], 1, 1)
# est = GLE_Estimator(init_params="random", EnforceFDT=False, OptimizeDiffusion=True, C_init=np.identity(2), A_init=np.array([[5, 1.0], [-2.0, 0.07]]), force_init=np.array([-1]), dim_x=dim_x, dim_h=dim_h, model=model)
X = basis.fit_transform(X)

est = GLE_Estimator(init_params="random", dim_x=dim_x, dim_h=dim_h, model=model, EnforceFDT=True, OptimizeDiffusion=True)
est.dt = X[1, 0] - X[0, 0]
est._check_initial_parameters()
est._check_n_features(X)

traj_list_h = np.split(Xh, idx)
# for n, traj in enumerate(traj_list_h):
#     traj_list_h[n] = traj_list_h[n][:-1, :]  # For euler

Xproc, idx = preprocessingTraj(X, idx_trajs=idx, dim_x=est.dim_x, model=model)
traj_list = np.split(Xproc, idx)

est._initialize_parameters(random_state=42)
datas = 0.0
for n, traj in enumerate(traj_list):
    datas_visible = sufficient_stats(traj, est.dim_x)
    zero_sig = np.zeros((len(traj), 2 * est.dim_h, 2 * est.dim_h))
    muh = np.hstack((np.roll(traj_list_h[n], -1, axis=0), traj_list_h[n]))
    # muh, Sigh = est._e_step(traj)  # Compute hidden variable distribution
    datas += sufficient_stats_hidden(muh, zero_sig, traj, datas_visible, est.dim_x, est.dim_h, est.dim_coeffs_force) / len(traj_list)
    # print(datas)

print(generator.get_coefficients())
logL1 = est.loglikelihood(datas)
est._m_step_num(datas)
logL2 = est.loglikelihood(datas)
print(logL1, logL2)
coeff_num = est.get_coefficients()
print("Num", coeff_num)
est._m_step(datas)
logL3 = est.loglikelihood(datas)
print(logL1, logL2 - logL1, logL3 - logL2)
print("Analytic", est.get_coefficients())
print("Diff")
anal_coef = est.get_coefficients()
for key, elem in coeff_num.items():
    print(key)
    print(elem - anal_coef[key])
