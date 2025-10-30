import pandas as pd
import matplotlib.pyplot as plt
import re

# === 設定中文字型 ===
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 微軟正黑體 (Windows)
plt.rcParams['axes.unicode_minus'] = False  # 避免負號亂碼

# === 讀取三個 CSV ===
df_irr = pd.read_csv("taiwan_solar_irradiance_2018_2024.csv")
df_temp = pd.read_csv("taiwan_solar_temp_monthly_2018_2024.csv")
df_power = pd.read_csv("taiwan_solar_power_2018_2024.csv")

# === 民國年月轉西元年月 ===
def convert_minguo_month(value):
    value = str(value).strip()
    match = re.match(r"(\d{3,4})(\d{2})", value)
    if match:
        year = int(match.group(1)) + 1911
        month = int(match.group(2))
        return f"{year}-{month:02d}"
    return None

df_power["year"] = df_power["year"].astype(str).str.replace("年", "", regex=False)
df_power["year_month_str"] = df_power["month"].apply(convert_minguo_month)
df_power["year_month"] = pd.to_datetime(df_power["year_month_str"], format="%Y-%m", errors="coerce")
df_power = df_power.dropna(subset=["year_month"]).drop_duplicates(subset=["year_month"]).sort_values(by="year_month")

# === 限定時間範圍 ===
start_date, end_date = pd.Timestamp("2018-01-01"), pd.Timestamp("2024-12-31")
df_power = df_power[(df_power["year_month"] >= start_date) & (df_power["year_month"] <= end_date)]
df_irr["year_month"] = pd.to_datetime(df_irr["year_month"], errors="coerce")
df_temp["year_month"] = pd.to_datetime(df_temp["year_month"], errors="coerce")
df_irr = df_irr[(df_irr["year_month"] >= start_date) & (df_irr["year_month"] <= end_date)]
df_temp = df_temp[(df_temp["year_month"] >= start_date) & (df_temp["year_month"] <= end_date)]

# === 全台平均 ===
df_irr_avg = df_irr.groupby("year_month")[["irradiance"]].mean().reset_index()
df_temp_avg = df_temp.groupby("year_month")[["temp_c"]].mean().reset_index()

# === 合併三個資料 ===
df_merged = pd.merge(df_power[["year_month", "power_kwh"]], df_irr_avg, on="year_month", how="inner")
df_merged = pd.merge(df_merged, df_temp_avg, on="year_month", how="inner")

# === Min-Max 歸一化 ===
for col in ["power_kwh", "irradiance", "temp_c"]:
    df_merged[f"{col}_norm"] = (df_merged[col] - df_merged[col].min()) / (df_merged[col].max() - df_merged[col].min())

# === 畫圖 ===
plt.figure(figsize=(12, 6))
plt.plot(df_merged["year_month"], df_merged["power_kwh_norm"], color="green", label="太陽能發電量")
plt.plot(df_merged["year_month"], df_merged["irradiance_norm"], color="orange", label="太陽輻照量")
plt.plot(df_merged["year_month"], df_merged["temp_c_norm"], color="red", label="平均氣溫")
plt.title("2018–2024 歸一化比較：太陽能發電量 vs 輻照量 vs 氣溫")
plt.xlabel("年份")
plt.ylabel("歸一化值（0–1）")
plt.legend()
plt.tight_layout()
plt.savefig("4_normalized_comparison.png", dpi=300)
plt.show()

print("✅ 已生成 4_normalized_comparison.png：三項歸一化比較圖。")
