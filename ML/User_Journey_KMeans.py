import yaml
import snowflake.connector
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import os
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
SELECT *
FROM ga4_user_journey_20260219
WHERE session_key IS NOT NULL
"""

# Create a cursor object, which will execute the query we defined above.
cursor = con.cursor()
# Execute the query.
cursor.execute(query)
# Store query results in a pandas DataFrame.
df = cursor.fetch_pandas_all()

df.head()
#%%
# choose features, clean, and scale 
import numpy as np
from sklearn.preprocessing import StandardScaler

ID_COLS = ["session_key", "user_pseudo_id"]  # adjust if your table uses different IDs
TARGET_COL = "converted"                     # adjust if named differently

# Pick numeric feature columns automatically
exclude = set([c for c in ID_COLS if c in df.columns] + ([TARGET_COL] if TARGET_COL in df.columns else []))
num_cols = [c for c in df.columns if c not in exclude and pd.api.types.is_numeric_dtype(df[c])]

print("Numeric feature columns:", num_cols)

X = df[num_cols].copy()

# Basic cleaning
X = X.replace([np.inf, -np.inf], np.nan)
# If you expect outliers: cap a few known columns (optional)
for col in X.columns:
    if col.startswith("rate_"):
        X[col] = X[col].clip(0, 1)
    if "seconds" in col:
        X[col] = X[col].clip(0, 300)

# Impute missing with median
X = X.fillna(X.median(numeric_only=True))

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

#%%
# pick reasonable K (5-10) using silhouette + inertia 

from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score

results = []
for k in range(5, 9):
    km = MiniBatchKMeans(n_clusters=k, batch_size=4096, n_init=10, max_iter=200, random_state=42)
    labels = km.fit_predict(X_scaled)

    sil = silhouette_score(
        X_scaled, labels,
        sample_size=min(20000, X_scaled.shape[0]),
        random_state=42
    )

    results.append({"k": k, "silhouette_approx": sil, "inertia": km.inertia_})

pd.DataFrame(results).sort_values("k")


#%% md
ASSIGN A K VALUE
#%%
from sklearn.cluster import MiniBatchKMeans

K = 7
final = MiniBatchKMeans(
    n_clusters=K,
    batch_size=4096,
    n_init=20,
    max_iter=300,
    random_state=42
)

df["persona_id"] = final.fit_predict(X_scaled)

df.head()

#%% md
SUMMARIZE CLUSTERS (upload csv into chatgpt to help you create persona names!)
#%%
# Cluster sizes
sizes = df.groupby("persona_id").size().rename("sessions").reset_index()

# Conversion rate by cluster
if TARGET_COL in df.columns:
    cvr = df.groupby("persona_id")[TARGET_COL].mean().rename("conversion_rate").reset_index()
else:
    cvr = pd.DataFrame({"persona_id": df["persona_id"].unique(), "conversion_rate": np.nan})

# Feature averages by cluster
feature_means = df.groupby("persona_id")[num_cols].mean().reset_index()

summary = sizes.merge(cvr, on="persona_id", how="left").merge(feature_means, on="persona_id", how="left")
summary = summary.sort_values("sessions", ascending=False)
summary

#%% md
To Help with Naming - compute below overall average
#%%
# overall = df[num_cols].mean(numeric_only=True)
# deltas = summary.set_index("persona_id")[num_cols].subtract(overall, axis=1)
# deltas
#%% md
Give Persona Human-Readable Names! 
#%%
import pandas as pd

persona_map = pd.DataFrame({
    "persona_id": [0, 1, 2, 3, 4, 5, 6],
    "persona_name": [
        "Light Browsers",
        "One-and-Done Bouncers",
        "High-Intent Power Buyers",
        "Researchers / Comparison Shoppers",
        "Cart Dabblers (High Add-to-Cart, Low Checkout)",
        "Search-Led Deep Browsers",
        "PDP Friction / Lost Buyers"
    ]
})

# df = df.merge(persona_map, on="persona_id", how="left")  # UNCOMMENT WHEN ADDING NEW PERSONA NAMES INTO THE EXISTING DF 
df.head()



#%% md

## Write results back to Snowflake
#%%
from snowflake.connector.pandas_tools import write_pandas

df.columns = df.columns.str.upper()


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
    table_name='GA4_USER_JOURNEY_PERSONAS_KMEANS_OUTPUT_20260219',
    use_logical_type=True,
    overwrite=True   ## THIS CREATES A NEW TABLE
    # overwrite=False   ## THIS ADDS TO EXISTING TABLE
)

print(f"Upload success: {success}, Rows uploaded: {nrows}")
