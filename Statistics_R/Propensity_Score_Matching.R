#### automation!!!!

# establishing file paths 
input_dir <- file.path("***", "Customer Group A-C")

output_file <- file.path("***", "final_results_customer_group_A.csv")


# creating an empty dataframe to append results to 
final_results_dataframe <- data.frame(
  pvalue = numeric(),
  data_week = character(),
  control1 = numeric(),
  control2 = numeric(),  
  treatment = numeric(),  
  matchedsize = numeric(),
  totalsize = integer()
  
)

# Get a list of all CSV files in the directory
csv_files <- list.files(input_dir, pattern = "\\.csv$", full.names = TRUE)


## LOOPING THROUGH!!! 

# Loop through each file
for (file_path in csv_files) {
  ############################################################ LOAD AND CLEAN DATA 
  
  # extracting the file name
  file_name <- basename(file_path)
  
  # print file name for debugging: 
  cat("processing file: ", file_name, "\n")
  
  # read in the csv file 
  customers <- read.csv(file_path)
  
  # loading up the libraries necessary 
  library(tidyverse)
  library(MatchIt)
  library(dplyr)
  library(ggplot2)
  
  # making all column names lowercase & printing them out 
  names(customers) <- base::tolower(names(customers))
  
  customers %>% 
    names()
  
  # filtering for specific customer grouping 
  customers <- subset(customers, customer_group == "A. Prior Buyer (Bought On Week)")
  # customers <- subset(customers, customer_group == "B. Prior Buyer (Did Not Buy On Week)")
  # customers <- subset(customers, customer_group == "C. First Time Buyer (Bought On Week)")
  # customers <- subset(customers, customer_group == "D. Non-Buyer (Email/BIS Signup On Week)")
  
  customers %>% 
    count()
  
  #filtering for US customers only 
  customers <- subset(customers, intl_flag == 0)
  
  customers %>% 
    count()
  
  # casting zip code as numeric: 
  customers$zip <- as.numeric(customers$zip)
  
  # dropping rows with missing values (NA)
  sum(complete.cases(customers) == FALSE)
  customers_clean <- na.omit(customers)
  sum(complete.cases(customers_clean) == FALSE)
  customers <- customers_clean
  
  
  ################################################################ WINSORIZE THE DATA 
  
  # Calculate the median and standard deviation
  mean_value <- mean(customers$post_sales, na.rm = TRUE)
  std_dev <- sd(customers$post_sales, na.rm = TRUE)
  print(mean_value)
  print(std_dev)
  
  # Calculate X as (median + 3 * standard deviation)
  X <- mean_value + 3 * std_dev
  print(X)
  
  # Replace values in column1 that are greater than X with X
  customers$post_sales <- ifelse(customers$post_sales > X, X, customers$post_sales)
  
  ################################################################ SUMMARIZE THE DATA  
  
  # view summary of the data 
  customers %>% 
    summary()
  
  # view count of non-members vs members
  customers %>% 
    group_by(loyalty_optin_flag) %>% 
    summarise(unique_count = n_distinct(email)) %>% 
    print()
  
  
  # calculating mean POST sales per customer by loyalty opt-in flag
  customers %>%
    group_by(loyalty_optin_flag) %>%
    summarise(mean_sales = mean(post_sales))
  
  
  ##  running a welch's two-sample t-test on POST sales per customer by loyalty opt-in flag
  pre_results <- with(customers, t.test(post_sales ~ loyalty_optin_flag))
  
  #################################################################### DATA PREP 
  
  # installing & loading package to create dummy variables for categorical data 
  # install.packages("fastDummies")
  library(fastDummies)
  
  
  # Create dummy variables for categorical columns
  customers_final <- dummy_cols(customers, select_columns = c('device_type'), remove_selected_columns = TRUE)
  
  
  # lowercase all the columns names again 
  names(customers_final) <- base::tolower(names(customers_final))
  
  
  # REMOVING UNNECESSARY COLUMNS
  customers_final <- subset(customers_final, select = -c(email, ios_device_flag, device_type_unknown, device_type_non_ios, 
                                                         bought_flag, session_rcy_days, customer_group, rcy_days, email_bis_signup_flag, 
                                                         weeks_since_first_interaction))   
  customers_final <- na.omit(customers_final)
  
  
  # viewing & summarizing the data before beginning PSM
  customers_final %>% 
    summary()
  customers_final %>% 
    names()
  customers_final %>% 
    count()
  
  #################################################################### PROPENSITY SCORING
  
  # let's run a logistic regression using all columns and target as loyalty member 
  log_model <- glm(loyalty_optin_flag ~ age + gender_female_flag + hhinc_amt
                   + zip + intl_flag + first_purchase_markdown_flag + first_purchase_shapewear_flag
                   + pre_sales + sales_on_week  
                   + device_type_ios
                   , data = customers_final, family = binomial)
  summary(log_model) 
  
  # Out of curiosity, which covariates are the strongest predictors of joining the program?
  # higher coefficients indicates stronger 
  #importance <- varImp(log_model, scale = FALSE)
  #print(importance)
  
  # Get the propensity scores for each customer 
  customer_prs <- data.frame(pr_score = predict(log_model, type = "response"),
                             loyalty_optin_flag = log_model$model$loyalty_optin_flag)
  head(customer_prs)
  
  #################################################################### MATCHING PAIRS
  
  # creating pairs in the dataset 
  mod_match <- matchit(loyalty_optin_flag ~ age + gender_female_flag + hhinc_amt
                       + zip + intl_flag + first_purchase_markdown_flag + first_purchase_shapewear_flag
                       + pre_sales + sales_on_week  
                       + device_type_ios
                       , method = "nearest", data = customers_final)
  
  summary(mod_match)
  
  # creating a data frame with matching values 
  dta_m <- match.data(mod_match)
  sizing <- dim(dta_m)
  head(dta_m)
  
  #################################################################### RESULTS
  
  # comparing post-sales per customer across members vs. non-members
  final_results <- with(dta_m, t.test(post_sales ~ loyalty_optin_flag))
  
  
  # items to add into the csv (expected one row per csv file )
  
  # t-test p value (post treatment lift test vs control)
  p_value <- final_results$p.value[1]
  
  # csv file date 
  csv_date <- substr(file_path,51,60)
  week <- csv_date
  
  # pre-psm control - post sales amount 
  pre_psm_control <- unname(pre_results$estimate[1])
  
  # post-psm control - post sales amount 
  post_psm_control <- unname(final_results$estimate[1])
  
  # post psm treatment - post sales amount 
  post_psm_treatment <- unname(final_results$estimate[2])
  
  # matched sizing psm 
  matched_psm_group_size <- print((sizing / 2)[1])
  
  # total psm group sizing 
  total_psm_group_size <- print(sizing[1])
  
  results_df <- data.frame(
    pvalue = p_value,
    data_week = week,
    control1 = pre_psm_control,
    control2 = post_psm_control,  
    treatment = post_psm_treatment,  
    matchedsize = matched_psm_group_size,
    totalsize = total_psm_group_size
  )
  #print(results_df)

  #APPEND RESULTS INTO FINAL RESULTS DF 
  final_results_dataframe <- rbind(final_results_dataframe, results_df)
  
}

# Save the final results to a CSV file
write.csv(final_results_dataframe, output_file, row.names = FALSE)

# Print a confirmation message
cat("Results saved to:", output_file, "\n")



