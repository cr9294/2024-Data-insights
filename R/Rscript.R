# R脚本，用于进行贝叶斯分层逻辑回归，研究淡水和河流环境中海丽鳞鳗的雄性比例
# 与手稿相关的分析
# Johnson, N.S., W.D. Swink, and T.O. Brenden. In press. Field study suggests that sex determination in
# sea lamprey is directly influenced by larval growth rate. Proceedings of the Royal Society B.
# 代码仅供参考，不提供明示或暗示的保证。
# 代码最后由T. Brenden（MSU）和N. Johnson（USGS）修改 - 2017年2月28日

# 加载必要的库
library(R2jags)
library(runjags)

# 读入数据并将数值型位置标识符转换为因子变量
ratio <- read.table("data.csv", sep = ",", header = T)
ratio$Location <- as.factor(ratio$Location)

# 创建一个2x2单位矩阵作为Wishart分布的模糊先验的比例参数
R <- matrix(0, nrow = 2, ncol = 2)
diag(R) <- 1.0

# 创建一个包含过度分散的初始化值列表，用于进行MCMC分析
  # 三个不同的初始化值，用于进行MCMC分析
  # 每个初始化值包含模型中的参数，如斜率、截距、方差等
inits <- list(list(parms.lentic = c(-3, 1), parms.lotic = c(-3, 1), beta = c(0, 0, 0, 0, 0, 0, 0, 0), beta1 = c(0, 0, 0, 0, 0, 0, 0, 0), sigma.intercept = 0.01, sigma.slope = 0.01),
              list(parms.lentic = c(0, 0), parms.lotic = c(0, 0), beta = c(0, 0, 0, 0, 0, 0, 0, 0), beta1 = c(0, 0, 0, 0, 0, 0, 0, 0), sigma.intercept = 1.2, sigma.slope = 1.2),
              list(parms.lentic = c(3, -1), parms.lotic = c(3, -1), beta = c(0, 0, 0, 0, 0, 0, 0, 0), beta1 = c(0, 0, 0, 0, 0, 0, 0, 0), sigma.intercept = 10, sigma.slope = 10))

# 创建一个将用于拟合层次模型的数据列表
lamprey.data <- list(Years = ratio$Years, males = ratio$Male, streams = ratio$Location, N = nrow(ratio), R = R, mn = c(0, 0))

# 确定将对其进行后验概率分布特征化的参数和派生变量
lamprey.parms <- c("parms.lentic", "parms.lotic", "sigma.intercept", "sigma.slope", "predicted", "lentic", "lotic", "beta", "beta1")

# 指定用于拟合模型的JAGS代码
lamprey.model <- function() {

  # 指定模型参数的先验和超先验
  TAU[1:2, 1:2] ~ dwish(R[1:2, 1:2], 3)
  TAU2[1:2, 1:2] ~ dwish(R[1:2, 1:2], 3)
  parms.lentic[1:2] ~ dmnorm(mn, TAU)
  parms.lotic[1:2] ~ dmnorm(mn, TAU2)
  sigma.intercept ~ dunif(0, 100)
  tau.intercept <- 1 / (sigma.intercept * sigma.intercept)
  sigma.slope ~ dunif(0, 100)
  tau.slope <- 1 / (sigma.slope * sigma.slope)

  # 为分析淡水系统中的雄性百分比指定特定于位置的参数
  for (j in 1:3) {
    beta[j] ~ dnorm(parms.lentic[1], tau.intercept)
    beta1[j] ~ dnorm(parms.lentic[2], tau.slope)
  }
  # 为分析河流系统中的雄性百分比指定特定于位置的参数
  for (j in 4:8) {
    beta[j] ~ dnorm(parms.lotic[1], tau.intercept)
    beta1[j] ~ dnorm(parms.lotic[2], tau.slope)
  }

  # 指定模型似然性
  for (i in 1:N) {
    logit(p[i]) <- beta[streams[i]] + beta1[streams[i]] * Years[i]
    males[i] ~ dbern(p[i])
  }

  # 预测从标记后0到7年每个位置的雄性百分比
  for (k in 1:7) {
    logit(lentic[k]) = parms.lentic[1] + parms.lentic[2] * (k - 1)
    logit(lotic[k]) = parms.lotic[1] + parms.lotic[2] * (k - 1)
    logit(predicted[k, 1]) = beta[1] + beta1[1] * (k - 1)
    logit(predicted[k, 2]) = beta[2] + beta1[2] * (k - 1)
    logit(predicted[k, 3]) = beta[3] + beta1[3] * (k - 1)
    logit(predicted[k, 4]) = beta[4] + beta1[4] * (k - 1)
    logit(predicted[k, 5]) = beta[5] + beta1[5] * (k - 1)
    logit(predicted[k, 6]) = beta[6] + beta1[6] * (k - 1)
    logit(predicted[k, 7]) = beta[7] + beta1[7] * (k - 1)
    logit(predicted[k, 8]) = beta[8] + beta1[8] * (k - 1)
  }
}

# 指定用于可重复性的随机种子
set.seed(302563)

# 运行JAGS模型，打印结果，并将结果转换为.mcmc对象
jags.model <- jags(lamprey.data, inits = inits, parameters.to.save = lamprey.parms, n.chains = 3, n.iter = 2000000, n.burnin = 1000000, n.thin = 100, model.file = lamprey.model)
print(jags.model)
mcmc.model <- as.mcmc(jags.model)

# 更改绘图参数并生成跟踪图和密度图
par(mar = c(2.5, 3, 2, 1), mfrow = c(3, 3))
traceplot(mcmc.model)
densplot(mcmc.model)

# 计算规模缩减因子以评估3个链是否收敛到相似的分布
gelman.diag(mcmc.model)

# 将3个链的保存迭代合并成单个链
mcmc.combined <- combine.mcmc(mcmc.model)

# 从保存的MCMC链中获取中位数
mcmc.summary <- summary(mcmc.combined)
mcmc.summary

# 从保存的MCMC链中获取最高后验密度间隔
mcmc.HPD <- HPDinterval(mcmc.combined)
mcmc.HPD

# 计算概率男性比例在淡水环境中大于河流环境的可能性，根据保存的MCMC链计算不同时间段
year0 <- mcmc.combined[, 18] > mcmc.combined[, 25]
sum(year0) / length(year0)
year1 <- mcmc.combined[, 19] > mcmc.combined[, 26]
sum(year1) / length(year1)
year2 <- mcmc.combined[, 20] > mcmc.combined[, 27]
sum(year2) / length(year2)
year3 <- mcmc.combined[, 21] > mcmc.combined[, 28]
sum(year3) / length(year3)
year4 <- mcmc.combined[, 22] > mcmc.combined[, 29]
sum(year4) / length(year4)
year5 <- mcmc.combined[, 23] > mcmc.combined[, 30]
sum(year5) / length(year5)
year6 <- mcmc.combined[, 24] > mcmc.combined[, 31]
sum(year6) / length(year6)
