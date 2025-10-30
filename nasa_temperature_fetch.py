import requests
import pandas as pd
from tqdm import tqdm

# 全台主要太陽能設置縣市與座標
LOCATIONS = {
    "Taipei": (25.05, 121.52),
    "Taoyuan": (24.99, 121.31),
    "Hsinchu": (24.81, 120.97),
    "Miaoli": (24.56, 120.82),
    "Taichung": (24.15, 120.67),
    "Changhua": (24.08, 120.54),
    "Yunlin": (23.71, 120.54),
    "Chiayi": (23.48, 120.44),
    "Tainan": (23.0, 120.2),
    "Kaohsiung": (22.63, 120.3),
    "Pingtung": (22.67, 120.48),
    "Taitung": (22.76, 121.14),
    "Hualien": (23.98, 121.61),
}

START = "20180101"  
END   = "20241231"
PARAMS = "ALLSKY_SFC_SW_DWN,T2M"
COMMUNITY = "RE"

def fetch_daily_data(lat, lon):
    """從 NASA POWER daily API 下載太陽輻射與溫度資料"""
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters={PARAMS}&community={COMMUNITY}"
        f"&latitude={lat}&longitude={lon}"
        f"&start={START}&end={END}&format=JSON"
    )
    resp = requests.get(url, timeout=60)
    if resp.status_code != 200:
        print(f"無法取得資料 ({resp.status_code}) - {url}")
        return pd.DataFrame()

    data = resp.json()
    try:
        irr = data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
        tmp = data["properties"]["parameter"]["T2M"]
    except KeyError:
        print("回傳資料格式錯誤，略過。")
        return pd.DataFrame()

    df = pd.DataFrame({
        "date": pd.to_datetime(list(irr.keys())),
        "irradiance": list(irr.values()),
        "temp_c": list(tmp.values())
    })
    return df

# === 主程式 ===
all_data = []
for name, (lat, lon) in tqdm(LOCATIONS.items(), desc="抓取中"):
    print(f"抓取 {name} ({lat}, {lon}) ...")
    df = fetch_daily_data(lat, lon)
    if not df.empty:
        df["location"] = name
        all_data.append(df)

if not all_data:
    raise RuntimeError("沒有任何地點成功抓取資料。")

# 合併所有城市
df_all = pd.concat(all_data)
df_all["year_month"] = df_all["date"].dt.to_period("M")

# 計算每月平均
df_monthly = df_all.groupby(["year_month", "location"]).mean().reset_index()
df_monthly["year"] = df_monthly["year_month"].dt.year
df_monthly["month"] = df_monthly["year_month"].dt.month

# 全台平均（非加權）
df_tw = df_monthly.groupby("year_month")[["irradiance", "temp_c"]].mean().reset_index()

# 儲存
df_all.to_csv("taiwan_solar_temp_daily_2018_2024.csv", index=False, encoding="utf-8-sig")
df_monthly.to_csv("taiwan_solar_temp_monthly_2018_2024.csv", index=False, encoding="utf-8-sig")
df_tw.to_csv("taiwan_avg_solar_temp_2018_2024.csv", index=False, encoding="utf-8-sig")

print("已完成所有資料下載與彙整！")
print(df_tw.head())
