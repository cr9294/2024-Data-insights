import numpy as np
import matplotlib.pyplot as plt

#plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
#plt.rcParams["axes.unicode_minus"] = False  # 该语句解决图像中的“-”负号的乱码问题

# 定义模型参数
R = 0.1        # 生长率
lambda_predator = 0.2  # 捕食系数
lambda_parasite = 0.3  # 寄生系数
f_G = 0.4      # G函数参数

# 定义个体数量
N_male = 10
N_female = 10

# 定义时间步长
dt = 0.1

# 定义初始个体数量
male0 = np.random.rand(N_male)
female0 = np.random.rand(N_female)

# 定义模型方程
def G(x):
    return x / (1 + x)

def f_male(N_male, N_predator):
    return R * G(f_G) - lambda_predator * N_predator * N_male

def f_female(N_female, N_parasite):
    return R * (1 - G(f_G)) - lambda_parasite * N_parasite * N_female

# 使用欧拉方法数值求解模型方程
t = 0
male = male0
female = female0
N_predator = np.random.rand()  # Initial predator population
N_parasite = np.random.rand()  # Initial parasite population

t_list = [t]
male_list = [male]
female_list = [female]

for i in range(1000):
    male_dot = f_male(male, N_predator)
    female_dot = f_female(female, N_parasite)

    male = male + male_dot * dt
    female = female + female_dot * dt

    t = t + dt
    t_list.append(t)
    male_list.append(male)
    female_list.append(female)

# 绘制个体数量随时间的变化曲线
fig, ax = plt.subplots()
ax.plot(t_list, male_list, label='Male')
ax.plot(t_list, female_list, label='Female')
ax.set_xlabel('time')
ax.set_ylabel('number of individuals')
ax.legend()
ax.set_title('Population')
plt.show()
