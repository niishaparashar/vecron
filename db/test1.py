import pandas as pd

file_path = "opportunity.csv"

df = pd.read_csv(file_path)

category_map = {
    "Data": "Analytics & AI",
    "Engineering": "Software Engineering",
    "Operations": "Infrastructure",
    "Product": "Business & Strategy"
}

df["category"] = df["department"].map(category_map)

# sanity check
if df["category"].isna().any():
    print("⚠️ Unmapped departments found:")
    print(df[df["category"].isna()]["department"].unique())
else:
    print("✅ Category column fixed successfully")

# overwrite the same file
df.to_csv(file_path, index=False)
print("💾 opportunity.csv has been updated in place.")
