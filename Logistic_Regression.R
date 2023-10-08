# ISE 225 - Engineering Statistics 
# LOGISTIC REGRESSION

# Part 1: Loading cars data & assigning binary values based on above/below median gross horsepower

data(mtcars)
?mtcars
median(mtcars$hp)

mtcars$hp_cat <- NA
mtcars$hp_cat[mtcars$hp<=123] <- 0
mtcars$hp_cat[mtcars$hp>123] <- 1


# Part 2: Fitting a logistic regression model with predictor = mpg, output = horsepower

glm.fit1 <- glm(hp_cat ~ mpg, data = mtcars, family = binomial)

summary(glm.fit1)


# Part 3: Odds ratio - is the odds ratio significant at a value of 0.01?

odds.ratio <- exp(-1.0693)
odds.ratio


# Part 4: Select 22 samples for training and the rest for testing
# Fit the model again by only using the training set and summarize the data 

set.seed(100)

train <- sample(32, 22)
train

mtcars.test <- mtcars[-train,]
mtcars.test
nrow(mtcars.test)


glm.fit.train <- glm(hp_cat~mpg, data = mtcars, family = binomial, subset = train)
summary(glm.fit.train)


# Part 5: Use the new fitted model for prediction
# Generate the confusion matrix and calculate the error rate 

glm.prob <- predict(glm.fit.train, newdata = mtcars.test, type = "response")
glm.prob
glm.pred <- rep(0, length(glm.prob))
glm.pred[glm.prob>0.5] <- 1
glm.pred[1:10]

table(glm.pred, mtcars.test$hp_cat)

error.rate <- 1/(6+1+3)
error.rate






