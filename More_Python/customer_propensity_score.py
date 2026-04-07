import yaml
import snowflake.connector
import seaborn as sns
import matplotlib.pyplot as plt
from lifetimes import BetaGeoFitter
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas

# pulling snowflake login info
with open('secrets.yaml', 'r') as f:
    secrets = yaml.safe_load(f)['snowflake_secrets']

# login credentials
PASSWORD = secrets["PASSWORD"]
WAREHOUSE = secrets["WAREHOUSE"]
ACCOUNT = secrets["ACCOUNT"]
USER = secrets["USER"]

# setting up connection
con = snowflake.connector.connect(
    user=USER,
    password=PASSWORD,
    account=ACCOUNT,
    warehouse=WAREHOUSE,
    database='***',
    schema='***'
    )

# pulling in customer data
query = """
with base as (
    select email
         , customer_id
         , min(created_at_pst::date)                                     as init_date
         , max(created_at_pst::date)                                     as rcy_date
         , count(distinct order_id)                                      as order_qty
         , sum(n_sales)                                                  as n_sales
    from **ORDERS**
    where orderline_excludefromsales_flag = 0
    and created_at_pst::date < current_date()
    group by all
)
select email
         , customer_id as shopify_id
         , init_date
         , rcy_date
         , order_qty
         , n_sales
         , (datediff('day', init_date, current_date()))                  as t
         , order_qty -  1                                                as frequency
         , iff(order_qty = 1, 0, (datediff('day', init_date, rcy_date))) as recency
         , t-recency                                                     as recency_from_today
         , n_sales/order_qty                                             as monetary_value
from base
group by all
"""

cursor = con.cursor()

cursor.execute(query)

df = cursor.fetch_pandas_all()


df = df.rename(columns={"EMAIL": "email", "SHOPIFY_ID": "shopify_id", "FREQUENCY": "frequency", "T": "T", "RECENCY": "recency", "RECENCY_FROM_TODAY": "recency_from_today", "MONETARY_VALUE": "monetary_value"})

model_cols = ['frequency', 'recency', 'T']

for col in model_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)

df = df.dropna(subset=['frequency', 'recency', 'T'])

bgf = BetaGeoFitter(penalizer_coef=0.0)

bgf.fit(df['frequency'], df['recency'], df['T'])

df['p_alive'] = bgf.conditional_probability_alive(df['frequency'], df['recency'], df['T'])

# adjusting p(alive) scores to improve accuracy for 1 time buyers
def adjusted_p_alive(row):
    if row['frequency'] == 0:
        decay_factor = max(1 - ((row['T'] - row['recency']) / row['T']), 0)
        # Optional: square the decay to make it drop off faster
        decay_factor = decay_factor ** 2
        return row['p_alive'] * decay_factor
    else:
        return row['p_alive']


df['p_alive_adjusted'] = df.apply(adjusted_p_alive, axis=1)

current_timestamp = datetime.now(ZoneInfo("America/Los_Angeles"))

df['run_datetime'] = current_timestamp

df['model_version'] = 'bgnbd_v1_2026-03-30'

df['propensity_score'] = df['p_alive_adjusted']cursor = con.cursor()

cursor.execute(query)

df = cursor.fetch_pandas_all()


df = df.rename(columns={"EMAIL": "email", "SHOPIFY_ID": "shopify_id", "FREQUENCY": "frequency", "T": "T", "RECENCY": "recency", "RECENCY_FROM_TODAY": "recency_from_today", "MONETARY_VALUE": "monetary_value"})

model_cols = ['frequency', 'recency', 'T']

for col in model_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)

df = df.dropna(subset=['frequency', 'recency', 'T'])

bgf = BetaGeoFitter(penalizer_coef=0.0)

bgf.fit(df['frequency'], df['recency'], df['T'])

df['p_alive'] = bgf.conditional_probability_alive(df['frequency'], df['recency'], df['T'])

# adjusting p(alive) scores to improve accuracy for 1 time buyers
def adjusted_p_alive(row):
    if row['frequency'] == 0:
        decay_factor = max(1 - ((row['T'] - row['recency']) / row['T']), 0)
        # Optional: square the decay to make it drop off faster
        decay_factor = decay_factor ** 2
        return row['p_alive'] * decay_factor
    else:
        return row['p_alive']


df['p_alive_adjusted'] = df.apply(adjusted_p_alive, axis=1)

current_timestamp = datetime.now(ZoneInfo("America/Los_Angeles"))

df['run_datetime'] = current_timestamp

df['model_version'] = 'bgnbd_v1_2026-03-30'

df['propensity_score'] = df['p_alive_adjusted']

pd.set_option('display.max_columns', None)  # Show all columns

print(df)




# setting up connection -- WRITING DF TO A TABLE IN SNOWFLAKE
con_2 = snowflake.connector.connect(
    user=USER,
    password=PASSWORD,
    account=ACCOUNT,
    warehouse=WAREHOUSE,
    database='***',
    schema='***'
    )

# 3. Write the dataframe to Snowflake
success, nchunks, nrows, _ = write_pandas(
    conn=con_2,
    df=df,
    table_name='CUSTOMER_PROPENSITY_SCORES_STG',
    use_logical_type=True,
    overwrite=True
)

print(f"Upload success: {success}, Rows uploaded: {nrows}")
