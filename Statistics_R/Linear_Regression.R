# ISE 225 - Engineering Statistics
# LINEAR REGRESSION


# Part 1: Load the wage data & generate a histogram

library(ISLR)

data("Wage")

?Wage

hist(Wage$wage)

# The data is left-skewed, suggesting that it is more common to have a below average wage. 


# Part 2: Log-transform the wage data, fit a simple linear regression, & summarize the data

log.wage <- log(Wage$wage)

lm.fit_log.wage_age <- lm(log.wage~age, data=Wage)

summary(lm.fit_log.wage_age)


# Part 3: Generate the residuals plot

plot(lm.fit_log.wage_age)

# The residuals plot suggests that there is a relationship between the residuals and their predicted outputs
# meaning we cannot assume that the relationship is linear.


# Part 4: Add age to the simple linear regression model

lm.fit_log.wage_2ndorder <- lm(log.wage~age+I(age^2), data=Wage)

summary(lm.fit_log.wage_2ndorder)


# Part 5:  Conducting a forward selection and decide which are the best predictors of wage. 

library(leaps)
install.packages("glmnet")
library(glmnet)

?Wage

forward.selection <- regsubsets(log.wage~ age+ year+ maritl+ race+ education+ jobclass+ health+ health_ins,  
                                  data = Wage, method = "forward", nvmax = 4)
summary(forward.selection)


# Part 6: Preparing the data for a Lasso Feature Selection

set.seed(123)

y <- log.wage
x <- model.matrix(log.wage~ age+ year+ maritl+ race+ education+ jobclass+ health+ health_ins, Wage)[,-1]

train <- sample(1: nrow(Wage), 0.7*nrow(Wage))
train
x.test <- x[-train,]
y.test <- y[-train]



# Part 7: Conducting a Lasso Analysis to select the best features 

grid <- 10^seq(10, -2, length=100)
lasso <- glmnet(x[train,], y[train], alpha=1, lambda = grid)
plot(lasso)

# cv to get best lambda
cv.lambda <- cv.glmnet(x[train,],y[train],alpha=1)
plot(cv.lambda)

# best lambda value:
bestlam <- cv.lambda$lambda.min
bestlam

# best lambda  for prediction
lasso.prediction <- predict(lasso, s=bestlam, newx = x.test)
mean((y.test-lasso.prediction)^2)


