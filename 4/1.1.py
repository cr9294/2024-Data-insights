import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# 定义方程
def model(z, t, r, K, C, a, b):
    P, F = z
    dPdt = r * P * (1 - P / K) - C * P * F
    dFdt = a * F - b * P * F
    return [dPdt, dFdt]

# 参数
r = 0.1  # 海蟒鳗鱼的最大增长率
K = 1000  # 环境承载量
C = 0.01  # 海蟒鳗鱼消耗食物资源的效率
a = 0.05  # 食物资源的自然增长率
b = 0.02  # 食物资源被海蟒鳗鱼消耗的效率

# 初始条件
P0 = 40  # 初始海蟒鳗鱼种群密度
F0 = 800  # 初始食物资源丰富程度
z0 = [P0, F0]

# 时间点
t = np.linspace(0, 200, 400)

# 求解ODE
sol = odeint(model, z0, t, args=(r, K, C, a, b))

# 绘图
plt.figure(figsize=(10, 5))
plt.plot(t, sol[:, 0], label='Sea Lamprey Population')
plt.plot(t, sol[:, 1], label='Food Resource')
plt.legend()
plt.xlabel('Time')
plt.ylabel('Population')
plt.title('Sea Lamprey and Food Resource Over Time')
plt.show()