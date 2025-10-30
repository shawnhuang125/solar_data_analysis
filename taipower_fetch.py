# 匯入 Selenium 與相關模組
from selenium import webdriver  # 控制 Chrome 瀏覽器
from selenium.webdriver.chrome.service import Service  # 管理 ChromeDriver 服務
from selenium.webdriver.chrome.options import Options  # 設定瀏覽器啟動選項
from selenium.webdriver.common.by import By  # 元素定位方式（By.ID, By.CSS_SELECTOR 等）
from selenium.webdriver.support.ui import Select, WebDriverWait  # 處理下拉選單,顯性等待
from selenium.webdriver.support import expected_conditions as EC  # 定義等待條件
from webdriver_manager.chrome import ChromeDriverManager  # 自動下載 / 管理 ChromeDriver
import pandas as pd  # 處理表格資料
import re  # 正則表達式，用來擷取數字
import time  # 加入延遲等待用

# 基本設定
# 台電再生能源發電量圖表網址（iframe 內容頁）
url = "https://www.taipower.com.tw/chart/b20_%E7%99%BC%E9%9B%BB%E8%B3%87%E8%A8%8A_%E5%86%8D%E7%94%9F%E8%83%BD%E6%BA%90%E7%99%BC%E9%9B%BB%E6%A6%82%E6%B3%81_%E6%9C%AC%E5%85%AC%E5%8F%B8%E8%BF%9112%E5%80%8B%E6%9C%88%E5%A4%AA%E9%99%BD%E5%85%89%E9%9B%BB%E7%99%BC%E9%9B%BB%E9%87%8F_.html?251022"

# 瀏覽器設定
chrome_options = Options()
chrome_options.add_argument("--headless")      # 啟用無頭模式,不開視窗
chrome_options.add_argument("--disable-gpu")   # 停用 GPU 加速,避免顯示錯誤

# 使用 webdriver-manager 自動安裝,啟動 ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 開啟目標網址
driver.get(url)

# 建立顯性等待物件（最長等待 10 秒）
wait = WebDriverWait(driver, 10)

# 等待年份下拉選單出現
# 頁面載入是動態生成的，要先等 <select id="selectPeriod"> 出現
wait.until(EC.presence_of_element_located((By.ID, "selectPeriod")))

# 建立 Select 物件,用來操作年份下拉選單
select = Select(driver.find_element(By.ID, "selectPeriod"))

# 用來儲存所有年份的資料
all_data = []

# 逐年爬取資料
for opt in select.options:
    year_value = opt.get_attribute("value")  # 取得 option 的值（例如 "113"）
    year_text = opt.text.strip()             # 取得顯示文字（例如 "113年"）

    # 跳過近12個月這個項目
    if year_value == "0":
        continue

    print(f"抓取 {year_text} ...")

    # 選擇該年份
    select.select_by_value(year_value)
    
    # 等待 2 秒,讓 amCharts 圖表更新完成
    time.sleep(2)

    # 等待所有圖表的 <g aria-label=""> 標籤生成
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "g[aria-label]")))

    # 取得所有含有發電資訊的 <g> 標籤
    g_tags = driver.find_elements(By.CSS_SELECTOR, "g[aria-label]")

    # 解析每個標籤的 aria-label 屬性
    for g in g_tags:
        label = g.get_attribute("aria-label")
        # 用正則擷取「月份」與「發電量」
        match = re.search(r"(\d{5})\s([\d,]+)", label)
        if match:
            month = match.group(1)  
            power = match.group(2).replace(",", "")  # 移除數字中的逗號
            all_data.append({
                "year": year_text,      # 年份文字
                "month": month,         # 月份代碼
                "power_kwh": int(power) # 轉換成整數的發電量
            })

# 關閉瀏覽器
driver.quit()

# 轉成 DataFrame 並匯出 CSV
df = pd.DataFrame(all_data)  # 轉成 pandas 資料表
df.to_csv("taiwan_solar_power_2018_2024.csv", index=False, encoding="utf-8-sig")  # 儲存為 CSV 檔
print("已儲存 taiwan_solar_power_2018_2024.csv")
