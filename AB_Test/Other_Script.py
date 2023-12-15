import pandas as pd
import numpy as np
import datetime
import pytz
from scipy import stats
import snowflake.connector
import os
from snowflake.connector.pandas_tools import write_pandas

'''
Stats Reminders:
H0 = no significant difference between the two groups (control/off vs treatment/on)
HA = there is a statistically significant difference between the two groups
If p < alpha then you can reject the null hypothesis
'''

# logging update times
pacific_tz = pytz.timezone('US/Pacific')
current_time = datetime.datetime.now(pacific_tz)
formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')


# PLUG INPUT DATA INTO QUERY VARIABLE + SNOWFLAKE LOGIN INFO
# prepping for snowflake connection
query = """
with
show_stats as (
    select case when show_start_datetime::date < '2023-08-21' then 'Pre'
            when show_start_datetime::date >= '2023-08-21' then 'Post' end as pre_post_filter
            , *
    from analytics.ntwrk_dw.f_show_stats
    where (
        festival_name = 'Sneaker Happy Hour'
            OR
        festival_name = '25 Days of Sneakers & Streetwear'
        )
)
select pre_post_filter
     , show_id
     , show_title
     , creator_list
     , pre_show_reach
     , live_viewers
     , demand_rate
     , product_revenue
     , customers
     , new_customers
from show_stats
"""

os.environ['SNOWFLAKE_USER'] = 'adreanna'
os.environ['SNOWFLAKE_PW'] = 'sandorwefalnanknea4NTWRK'
os.environ['SNOWFLAKE_ACCOUNT'] = 'ueb32119.us-east-1'


# INPUT TEST VARIABLE INFORMATION FOR TEST
# please reference the input data directly to plug in below -- this will be case-sensitive
ab_test_name = 'SHH-pre-post-show-tile'
alpha = 0.10
test_metric_name1 = "PRE_SHOW_REACH"
test_metric_name2 = "LIVE_VIEWERS"
test_metric_name3 = "DEMAND_RATE"
variation_column_name = "PRE_POST_FILTER"
variation_off_identifier = "Pre"
variation_on_identifier = "Post"

# # INPUT FOR DATAFRAME FILTERING
# data_filter_column_name = "VIEW_SHOW_STATE"
# filter_for = "Pre Show"


def metric_1_test(input_data):
    with snowflake.connector.connect(
            user=os.environ.get("SNOWFLAKE_USER"),
            password=os.environ.get("SNOWFLAKE_PW"),
            account=os.environ.get("SNOWFLAKE_ACCOUNT"),
            role="ANALYZER_ROLE",
    ) as conn:
        cursor = conn.cursor()
        cursor.execute(input_data)
        df1 = cursor.fetch_pandas_all()

        # # filtering for pre-show data only
        # df_1 = df1[df1[data_filter_column_name] == filter_for]

        # if you don't want your data to be filtered
        # then uncomment this line and comment out the one above^
        df_1 = df1

        # Separating control from treatment
        control_group_1 = df_1[df_1[variation_column_name] == variation_off_identifier]
        treatment_group_1 = df_1[df_1[variation_column_name] == variation_on_identifier]

        # Extract test metric
        control_data_1 = control_group_1[test_metric_name1]
        treatment_data_1 = treatment_group_1[test_metric_name1]

        # Summary statistics for each group
        control_mean_1 = np.mean(control_data_1)
        control_std_1 = np.std(control_data_1)
        treatment_mean_1 = np.mean(treatment_data_1)
        treatment_std_1 = np.std(treatment_data_1)

        # confidence level based on alpha
        ci_1 = (1 - alpha) * 100

        # Perform the t-test
        t_stat_1, p_value_1 = stats.ttest_ind(control_data_1, treatment_data_1)

        # Interpret the results
        if p_value_1 < alpha:
            text_output_1 = (f"Reject the null hypothesis: There is a significant difference"
                              f"between the groups at a {ci_1}% confidence level.")

        else:
            text_output_1 = (f"Fail to reject the null hypothesis: There is no "
                              f"significant difference between the groups at a {ci_1}% confidence level.")

        # tabular output - first row
        metric_1_values = [ab_test_name, formatted_time, test_metric_name1, control_mean_1, control_std_1,
                           treatment_mean_1, treatment_std_1, t_stat_1, p_value_1, ci_1, text_output_1]

        return metric_1_values


def metric_2_test(input_data):

    with snowflake.connector.connect(
            user=os.environ.get("SNOWFLAKE_USER"),
            password=os.environ.get("SNOWFLAKE_PW"),
            account=os.environ.get("SNOWFLAKE_ACCOUNT"),
            role="ANALYZER_ROLE",
    ) as conn:
        cursor = conn.cursor()
        cursor.execute(input_data)
        df_2 = cursor.fetch_pandas_all()

        # Separating control from treatment
        control_group_2 = df_2[df_2[variation_column_name] == variation_off_identifier]
        treatment_group_2 = df_2[df_2[variation_column_name] == variation_on_identifier]

        # Extract test metric column
        control_data_2 = control_group_2[test_metric_name2]
        treatment_data_2 = treatment_group_2[test_metric_name2]

        # Summary statistics for each group
        control_mean_2 = np.mean(control_data_2)
        control_std_2 = np.std(control_data_2)
        treatment_mean_2 = np.mean(treatment_data_2)
        treatment_std_2 = np.std(treatment_data_2)

        # confidence level based on alpha
        ci_2 = (1 - alpha) * 100

        # Perform the t-test
        t_stat_2, p_value_2 = stats.ttest_ind(control_data_2, treatment_data_2)

        # Interpret the results
        if p_value_2 < alpha:
            text_output_2 = (f"Reject the null hypothesis: There is a significant difference"
                               f"between the groups at a {ci_2}% confidence level.")

        else:
            text_output_2 = (f"Fail to reject the null hypothesis: There is no "
                               f"significant difference between the groups at a {ci_2}% confidence level.")

        # tabular output
        metric_2_values = [ab_test_name, formatted_time, test_metric_name2, control_mean_2, control_std_2,
                           treatment_mean_2, treatment_std_2, t_stat_2, p_value_2, ci_2, text_output_2]

        # print(ctr_values)
        return metric_2_values


def metric_3_test(input_data):

    with snowflake.connector.connect(
            user=os.environ.get("SNOWFLAKE_USER"),
            password=os.environ.get("SNOWFLAKE_PW"),
            account=os.environ.get("SNOWFLAKE_ACCOUNT"),
            role="ANALYZER_ROLE",
    ) as conn:
        cursor = conn.cursor()
        cursor.execute(input_data)
        df_3 = cursor.fetch_pandas_all()

        # Separating control from treatment
        control_group_3 = df_3[df_3[variation_column_name] == variation_off_identifier]
        treatment_group_3 = df_3[df_3[variation_column_name] == variation_on_identifier]

        # Extract test metric column
        control_data_3 = control_group_3[test_metric_name3]
        treatment_data_3 = treatment_group_3[test_metric_name3]

        # Summary statistics for each group
        control_mean_3 = np.mean(control_data_3)
        control_std_3 = np.std(control_data_3)
        treatment_mean_3 = np.mean(treatment_data_3)
        treatment_std_3 = np.std(treatment_data_3)

        # confidence level based on alpha
        ci_3 = (1 - alpha) * 100

        # Perform the t-test
        t_stat_3, p_value_3 = stats.ttest_ind(control_data_3, treatment_data_3)

        # Interpret the results
        if p_value_3 < alpha:
            text_output_3 = (f"Reject the null hypothesis: There is a significant difference"
                               f"between the groups at a {ci_3}% confidence level.")

        else:
            text_output_3 = (f"Fail to reject the null hypothesis: There is no "
                               f"significant difference between the groups at a {ci_3}% confidence level.")

        # tabular output
        metric_3_values = [ab_test_name, formatted_time, test_metric_name3, control_mean_3, control_std_3,
                           treatment_mean_3, treatment_std_3, t_stat_3, p_value_3, ci_3, text_output_3]

        # print(ctr_values)
        return metric_3_values


# taking the rows produced from the functions above and feeding them into this function
# combines the rows into a single dataframe
def combined_df(row1, row2, row3):
    column_names = ['AB_TEST_NAME', 'UPDATED_AT', 'METRIC_NAME', 'CONTROL_MEAN', 'CONTROL_STDEV', 'TREATMENT_MEAN'
                    , 'TREATMENT_STDDEV', 'T_STATISTIC', 'P_VALUE', 'CONFIDENCE_INTERVAL', 'TEXT_OUTPUT']

    ab_test_stats_df = pd.DataFrame(data=[row1, row2, row3], columns=column_names)

    return ab_test_stats_df


# writing the output dataframe into analytics.ntwrk_temps.ab_test_output
def write_to_snowflake(new_df):
    with snowflake.connector.connect(
            user=os.environ.get("SNOWFLAKE_USER"),
            password=os.environ.get("SNOWFLAKE_PW"),
            account=os.environ.get("SNOWFLAKE_ACCOUNT"),
            role="ANALYZER_ROLE",
            database="ANALYTICS",
            schema="NTWRK_TEMPS"
    ) as conn:
        success, nchunks, nrows, _ = write_pandas(conn, new_df, 'AB_TEST_OUTPUT')


df1 = metric_1_test(query)
df2 = metric_2_test(query)
df3 = metric_3_test(query)
df4 = combined_df(df1, df2, df3)
write_to_snowflake(df4)

# #  Testing out the DF:
# pd.set_option('display.max_columns', None)  # Display all columns
# print(df3)
