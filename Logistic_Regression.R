# ISE 225 - Engineering Statistics 
# LOGISTIC REGRESSION

# Part 1: Loading wage data and create a histogram

data(mtcars)
?mtcars
median(mtcars$hp)

mtcars$hp_cat <- NA
mtcars$hp_cat[mtcars$hp<=123] <- 0
mtcars$hp_cat[mtcars$hp>123] <- 1


# Part 2: 

glm.fit1 <- glm(hp_cat ~ mpg, data = mtcars, family = binomial)

summary(glm.fit1)


# Part 3: 

odds.ratio <- exp(-1.0693)
odds.ratio


# Part 4: 

set.seed(100)

train <- sample(32, 22)
train

mtcars.test <- mtcars[-train,]
mtcars.test
nrow(mtcars.test)


glm.fit.train <- glm(hp_cat~mpg, data = mtcars, family = binomial, subset = train)
summary(glm.fit.train)


# Part 5: 

glm.prob <- predict(glm.fit.train, newdata = mtcars.test, type = "response")
glm.prob
glm.pred <- rep(0, length(glm.prob))
glm.pred[glm.prob>0.5] <- 1
glm.pred[1:10]

table(glm.pred, mtcars.test$hp_cat)

error.rate <- 1/(6+1+3)
error.rate






