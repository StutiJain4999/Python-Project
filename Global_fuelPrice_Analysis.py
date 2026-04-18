import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

file_path = "C:/Users/pc/Downloads/python_dataset.xlsx"
sheets = pd.read_excel(file_path, sheet_name=None)
combined_data = []
for fuel_type, df in sheets.items():
    df.rename(columns={df.columns[0]: "Country"}, inplace=True)
    df_long = df.melt(id_vars="Country",
                      var_name="Date",
                      value_name="Price")
    df_long["Fuel_Type"] = fuel_type
    combined_data.append(df_long)
final_df = pd.concat(combined_data, ignore_index=True)
print(final_df.head())
print(final_df.shape)
final_df.to_excel("combined_fuel_dataset.xlsx", index=False)
print("Dataset combined successfully")


final_df.drop_duplicates(inplace=True)
final_df.drop_duplicates(inplace=True)
final_df["Date"] = pd.to_datetime(final_df["Date"], errors="coerce")
# Convert Price to numeric
final_df["Price"] = pd.to_numeric(final_df["Price"], errors="coerce")
# Fill missing values
final_df["Price"] = final_df["Price"].fillna(final_df["Price"].mean())
scaler = MinMaxScaler()
final_df["Price_Normalized"] = scaler.fit_transform(final_df[["Price"]])






#BARPLOT

sns.set_style("darkgrid")
plt.figure(figsize=(10,6))
fuel_avg = final_df.groupby("Fuel_Type")["Price"].mean().sort_values(ascending=False)

# Gradient palette
palette = sns.color_palette("viridis", len(fuel_avg))

sns.barplot(
    x=fuel_avg.index,
    y=fuel_avg.values,
    palette=palette,
    edgecolor="black"
)

plt.title("Average Fuel Price by Fuel Type", fontsize=14)
plt.xlabel("Fuel Type")
plt.ylabel("Average Price")

plt.xticks(rotation=30)
plt.show()




#LINECHART 

sns.set_style("darkgrid")
sns.set_context("talk")
plt.figure(figsize=(10,6))

# convert date
final_df["Date"] = pd.to_datetime(final_df["Date"])

# month extract
final_df["Month"] = final_df["Date"].dt.month_name().str[:3]

# month order
month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

monthly_avg = final_df.groupby("Month")["Price"].mean().reindex(month_order)

# line chart (color changed)
sns.lineplot(
    x=monthly_avg.index,
    y=monthly_avg.values,
    marker="o",
    linewidth=3,
    color="#E74C3C"   # red color instead of blue
)

plt.title("Average Fuel Price by Month")
plt.xlabel("Month")
plt.ylabel("Average Price")

plt.show()




#BOXPLOT

sns.set_style("darkgrid")
sns.set_context("talk")

plt.figure(figsize=(10,6))

# boxplot
sns.boxplot(
    y=final_df["Price"],
    color="#9B59B6",      # purple box
    width=0.3,
    flierprops=dict(marker='o', markerfacecolor='red', markersize=5, linestyle='none')
)

plt.title("Fuel Price - Outlier Detection")
plt.ylabel("Price")
plt.show()

Q1 = final_df["Price"].quantile(0.25)
Q3 = final_df["Price"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5*IQR
upper = Q3 + 1.5*IQR

print("IQR =", round(IQR,2))
print("Outlier range: below", round(lower,2), "or above", round(upper,2))








#HEATMAP

sns.set_style("darkgrid")
sns.set_context("talk")

# convert Date
final_df["Date"] = pd.to_datetime(final_df["Date"])

# Pivot table (Fuel types as columns)
fuel_pivot = final_df.pivot_table(
    values="Price",
    index="Date",
    columns="Fuel_Type"
)

# fill missing values
fuel_pivot = fuel_pivot.fillna(method="ffill")

# correlation matrix
corr = fuel_pivot.corr()

plt.figure(figsize=(10,8))

sns.heatmap(
    corr,
    annot=True,
    cmap="magma",
    linewidths=0.5,
    fmt=".2f",
    square=True,
    cbar_kws={"label":"Correlation"}
)

plt.title("Correlation Heatmap of Fuel Prices")
plt.show()




#PAIRPLOT


sns.set_style("darkgrid")
sns.set_context("talk")

# convert date
final_df["Date"] = pd.to_datetime(final_df["Date"])

# create numeric features
final_df["Month"] = final_df["Date"].dt.month

pair_df = final_df[["Price","Month","Fuel_Type"]].sample(2000, random_state=42)

# pairplot
g = sns.pairplot(
    pair_df,
    hue="Fuel_Type",
    diag_kind="kde",
    palette="magma",
    plot_kws={"alpha":0.7, "s":50}
)

g.fig.suptitle("Pairplot of Fuel Price Features", y=1.02)

plt.show()





#MACHINE LEARNING CONFUSION MATRIX

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

sns.set_style("darkgrid")
sns.set_context("talk")

# convert date
final_df["Date"] = pd.to_datetime(final_df["Date"])

# features
final_df["Year"] = final_df["Date"].dt.year
final_df["Month"] = final_df["Date"].dt.month

# remove missing values
final_df = final_df.dropna()

# create price category
median_price = final_df["Price"].median()

final_df["Price_Category"] = final_df["Price"].apply(
    lambda x: "Low" if x < median_price else "High"
)

# encode fuel type
df_ml = pd.get_dummies(final_df, columns=["Fuel_Type"], drop_first=True)

# features
X = df_ml[["Year","Month"] + [c for c in df_ml.columns if "Fuel_Type_" in c]]

# target
y = final_df["Price_Category"]

# split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# predictions
pred = model.predict(X_test)

# confusion matrix
cm = confusion_matrix(y_test, pred)

plt.figure(figsize=(6,5))

sns.heatmap(
    cm,
    annot=True,
    cmap="Blues",
    fmt="d",
    xticklabels=["Low Price","High Price"],
    yticklabels=["Low Price","High Price"]
)

plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()



#PIEPLOT

sns.set_style("darkgrid")

# count fuel types
fuel_counts = final_df["Fuel_Type"].value_counts()

plt.figure(figsize=(8,8))

plt.pie(
    fuel_counts,
    labels=fuel_counts.index,
    autopct="%1.1f%%",
    startangle=140,
    colors=sns.color_palette("magma", len(fuel_counts)),
    wedgeprops={"edgecolor":"white","linewidth":2}
)

plt.title("Fuel Type Distribution", fontsize=16)

plt.show()




import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_style("darkgrid")
sns.set_context("talk")

# convert date
final_df["Date"] = pd.to_datetime(final_df["Date"])

# create numeric features
final_df["Year"] = final_df["Date"].dt.year
final_df["Month"] = final_df["Date"].dt.month

# sample data for clear visualization
pair_df = final_df.sample(2000)

# pairplot
sns.pairplot(
    pair_df,
    vars=["Price","Year","Month"],
    hue="Fuel_Type",
    palette="magma",
    diag_kind="hist",
    plot_kws={"alpha":0.6,"s":40}
)

plt.suptitle("Pairplot of Fuel Price Features", y=1.02)

plt.show()





#CAMPARISON INDIA VS GLOBAL FUEL PRICES


india_data = final_df[final_df["Country"].str.contains("India", case=False)]

india_fuel = india_data.groupby("Fuel_Type")["Price"].mean()

global_fuel = final_df.groupby("Fuel_Type")["Price"].mean()

comparison = pd.DataFrame({
    "India": india_fuel,
    "Global Average": global_fuel
})

comparison.plot(kind="bar", figsize=(10,5), color=["red","blue"])

plt.title("India vs Global Fuel Prices by Fuel Type")
plt.xlabel("Fuel Type")
plt.ylabel("Average Price")
plt.show()


# Remove extreme outliers using quantile

#BOX PLOT

q_low = final_df["Price"].quantile(0.01)
q_high = final_df["Price"].quantile(0.99)

filtered_df = final_df[(final_df["Price"] >= q_low) & (final_df["Price"] <= q_high)]

plt.figure(figsize=(10,6))

sns.boxplot(
    x="Fuel_Type",
    y="Price",
    data=filtered_df,
    palette="Set2"
)
plt.title("Fuel Price Distribution Across Fuel Types")
plt.xlabel("Fuel Type")
plt.ylabel("Fuel Price")
plt.show()




#SCATTER PLOT

import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Fuel price range (controlled)
fuel_price = np.random.uniform(10, 200, 1500)

# Demand depends on price with randomness
fuel_demand = fuel_price * np.random.uniform(20, 50, 1500) + np.random.normal(0, 500, 1500)

plt.figure(figsize=(10,6))

plt.scatter(
    fuel_price,
    fuel_demand,
    color="royalblue",
    edgecolor="white",
    alpha=0.7
)

plt.title("Fuel Price vs Fuel Demand Relationship")

plt.xlabel("Fuel Price")
plt.ylabel("Fuel Demand")

plt.show()




#CAMPARISION CHART

# India data
india_data = final_df[final_df["Country"].str.contains("India", case=False, na=False)]

# Global average
global_trend = final_df.groupby("Date")["Price"].mean()

# India trend
india_trend = india_data.groupby("Date")["Price"].mean()

plt.figure(figsize=(10,5))

plt.plot(global_trend, label="Global Average", color="blue", linewidth=2)

plt.plot(india_trend, label="India", color="red", linewidth=2)

plt.title("India vs Global Fuel Price Trend")

plt.xlabel("Year")
plt.ylabel("Average Fuel Price")

plt.legend()

plt.show()





