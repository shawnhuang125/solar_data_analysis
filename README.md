# Taiwan Solar Power Data Visualization (2018–2024)

本專案旨在分析與視覺化 **2018 至 2024 年台灣地區的太陽能發電量、太陽輻射量與平均氣溫變化趨勢**，  
並透過 **歸一化 (Normalization)** 技術，使三種不同單位的資料能夠公平比較。

---

## 專案結構

```
solar_power/
│
├── data/
│   ├── taiwan_solar_power.csv        # 台電太陽能發電量資料
│   ├── taiwan_solar_radiation.csv    # NASA POWER API 太陽輻射量資料
│   ├── taiwan_temperature.csv        # NASA POWER API 平均氣溫資料
│
├── nasa_fetch.py                     # 抓取 NASA 太陽輻射與氣溫資料的程式
├── data_visualization.py             # 產生月度折線圖與歸一化比較圖
├── requirements.txt                  # 主要 Python 套件需求
└── README.md                         # 專案說明文件（本檔）
```

---

## 資料來源

1. **太陽能發電量**  
   來源：台灣電力公司再生能源發電資訊  
   https://www.taipower.com.tw/chart/

2. **太陽輻射量與氣溫**  
   來源：NASA POWER (Prediction of Worldwide Energy Resources) API  
   文件：https://power.larc.nasa.gov/docs/services/api/

---

## 使用方法

### 安裝環境

請先建立虛擬環境並安裝必要套件：

```bash
pip install -r requirements.txt
```

主要套件：

- `pandas`：資料處理  
- `matplotlib`：繪製折線圖  
- `requests`：抓取 NASA API 資料  
- `python-dotenv`：讀取環境變數  

---

### 抓取 NASA 資料

可在 `nasa_fetch.py` 設定目標座標（latitude、longitude）與年份範圍：

```python
LOCATIONS = {
    "Taipei": (25.05, 121.52),
    "Taichung": (24.15, 120.67),
    "Tainan": (23.00, 120.20),
    "Kaohsiung": (22.63, 120.30),
    "Hualien": (23.98, 121.61)
}

START_YEAR = 2018
END_YEAR = 2024
```

執行指令：

```bash
python nasa_fetch.py
```

成功後會在 `data/` 資料夾中生成 `taiwan_solar_radiation.csv` 與 `taiwan_temperature.csv`。

---

### 視覺化資料

執行下列程式產生折線圖：

```bash
python data_visualization.py
```

輸出結果包含：

- 各縣市的月度太陽能發電量折線圖  
- 月度太陽輻射量折線圖  
- 月度平均氣溫折線圖  
- 三者歸一化後的比較圖  

---

## 歸一化 (Normalization) 說明

為了比較不同單位的變數（例如 kWh、MJ/m²、°C），  
使用 **Min–Max Normalization** 將資料縮放至 0–1 區間：

\[
X' = \frac{X - X_{min}}{X_{max} - X_{min}}
\]

此過程會：

- 保留原始趨勢與比例（線性縮放）；  
- 移除原本單位；  
- 使不同變數能在同一張圖上比較變化趨勢。

---

## 結果分析摘要

- 2023–2024 年下半年，台灣太陽輻射量與氣溫均有下降趨勢。  
- 對應的太陽能發電量亦顯著減少，顯示可能存在輻射量與氣溫對發電效率的共同影響。  
- 但仍需更長期的觀測與氣象條件（如雲量、降雨）才能確立因果關係。

---

## 授權

本專案僅供教育與研究用途，資料來源屬原機構所有（台電、NASA POWER）。

---

作者：**Luchia Huang**  
更新日期：2025-10
