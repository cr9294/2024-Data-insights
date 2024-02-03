import numpy as np
import matplotlib.pyplot as plt

def lotka_volterra(N0, M0, r_N, r_M, K_N, K_M, a, b, dt, num_steps):
    N = np.zeros(num_steps + 1)
    M = np.zeros(num_steps + 1)

    N[0] = N0
    M[0] = M0

    for i in range(num_steps):
        dN = (r_N * N[i] * (1 - N[i] / K_N) - a * N[i] * M[i]) * dt
        dM = (r_M * M[i] * (1 - M[i] / K_M) - b * N[i] * M[i]) * dt

        N[i + 1] = N[i] + dN
        M[i + 1] = M[i] + dM

    return N, M

# 参数设置
N0 = 100  # 初始雌性数量
M0 = 50   # 初始雄性数量
r_N = 0.1  # 雌性种群增长率
r_M = 0.1  # 雄性种群增长率
K_N = 500  # 雌性种群容量
K_M = 300  # 雄性种群容量
a = 0.02   # 捕食率
b_low = 0.001  # 低资源时的捕食率
b_high = 0.005  # 高资源时的捕食率
dt = 0.1  # 时间步长
num_steps = 500  # 模拟步数

# 模拟低资源条件
N_low, M_low = lotka_volterra(N0, M0, r_N, r_M, K_N, K_M, a, b_low, dt, num_steps)

# 模拟高资源条件
N_high, M_high = lotka_volterra(N0, M0, r_N, r_M, K_N, K_M, a, b_high, dt, num_steps)

# 绘图
time = np.arange(0, num_steps * dt + dt, dt)

plt.figure(figsize=(10, 6))
plt.plot(time, N_low, label='Low Resource - Females')
plt.plot(time, M_low, label='Low Resource - Males')
plt.plot(time, N_high, label='High Resource - Females')
plt.plot(time, M_high, label='High Resource - Males')
plt.xlabel('Time')
plt.ylabel('Population')
plt.title('Lotka-Volterra Simulation')
plt.legend()
plt.show()
