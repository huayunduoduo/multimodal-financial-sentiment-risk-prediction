import time
import csv
import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def parse_pub_date(text, now):
    """
    解析发布时间字符串：
    1. 如果格式为 "YYYY-MM-DD" 或 "YYYY-MM-DD HH:MM:SS"，直接转换为 datetime 对象；
    2. 如果格式为 "MM-DD"，则假设年份为参考时间（now.year）。
    注意：本函数不处理相对时间，主循环中会直接过滤包含“小时前”、“天前”或“分钟前”的数据。
    """
    text = text.strip()
    # 尝试完整日期格式
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(text, fmt)
        except Exception:
            continue

    # 支持 "MM-DD" 格式，例如 "02-25"
    if re.match(r"^\d{2}-\d{2}$", text):
        try:
            month, day = map(int, text.split("-"))
            return datetime.datetime(now.year, month, day)
        except Exception:
            return None
    return None

def simulate_slow_scroll(driver, total_distance=1000, step=100, delay=0.5):
    """
    模拟慢速滚动：
    - total_distance: 本次滚动需要移动的总像素数
    - step: 每次滚动的步长（像素）
    - delay: 每次滚动后的等待时间（秒）
    """
    for _ in range(0, total_distance, step):
        driver.execute_script("window.scrollBy(0, arguments[0]);", step)
        time.sleep(delay)

# 定义发布时间区间含边界
lower_bound = datetime.datetime(2025, 5, 1)
upper_bound = datetime.datetime(2025, 10, 11)
# 用参考时间解析 MM-DD 格式，这里采用 upper_bound 的年份（即 2025）
reference_time = upper_bound

# 初始化 Chrome 浏览器驱动
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

# 打开初始页面并点击“股市”链接（href="/channel/10233"）
driver.get("https://www.cnstock.com/channel/10232")
link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/channel/10233']")))
link.click()
time.sleep(5)

data = []
processed_links = set()
stop_flag = False

max_no_new_count = 3
no_new_count = 0

while not stop_flag:
    # 获取当前页面所有项目（每个项目外层 a 标签 class 包含 "index_item__GpLlY"）
    items = driver.find_elements(By.CSS_SELECTOR, "a.index_item__GpLlY")
    current_count = len(items)

    # 遍历当前页面项目，提取数据
    for item in items:
        href = item.get_attribute("href")
        if href in processed_links:
            continue
        processed_links.add(href)
        try:
            title = item.find_element(By.CSS_SELECTOR, "h5.index_title__gKrkC").text.strip()
        except Exception:
            title = ""
        try:
            node_name = item.find_element(By.CSS_SELECTOR, "span.index_nodeName__haPOr").text.strip()
        except Exception:
            node_name = ""
        try:
            tag_name = item.find_element(By.CSS_SELECTOR, "span.index_tagName__DfcTE").text.strip()
        except Exception:
            tag_name = ""
        try:
            time_text = item.find_element(By.CSS_SELECTOR, "div.index_time__5xP5N").text.strip()
        except Exception:
            time_text = ""

        # 如果发布时间中包含相对时间关键字，则跳过该项
        if any(x in time_text for x in ["小时前","分钟前"]):
            continue

        pub_date = parse_pub_date(time_text, reference_time)
        if pub_date is None:
            continue

        # 如果遇到发布时间早于下界，则认为后续数据已不在目标区间，停止加载
        if pub_date < lower_bound:
            stop_flag = True
            break

        # 仅保存发布时间在 [2024-12-30, 2025-01-02] 范围内的数据（含边界）
        if lower_bound <= pub_date <= upper_bound:
            item_data = {
                "link": href,
                "title": title,
                "node_name": node_name,
                "tag_name": tag_name,
                "pub_date": pub_date.strftime("%Y-%m-%d %H:%M:%S")
            }
            data.append(item_data)
            # 实时打印当前爬取的数据
            print("爬取到数据：", item_data)
    if stop_flag:
        break

    # 模拟慢速滑动
    simulate_slow_scroll(driver, total_distance=1000, step=300, delay=0.5)
    time.sleep(2)  # 滑动后等待数据加载

    # 判断是否有新项目加载
    items = driver.find_elements(By.CSS_SELECTOR, "a.index_item__GpLlY")
    new_count = len(items)
    if new_count == current_count:
        no_new_count += 1
    else:
        no_new_count = 0
    if no_new_count >= max_no_new_count:
        break

# 保存数据到 CSV 文件
csv_file = "cnstock_data.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["link", "title", "node_name", "tag_name", "pub_date"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        writer.writerow(row)

print("共爬取数据 {} 条，数据已保存在文件：{}".format(len(data), csv_file))
input("请按回车键关闭浏览器...")
driver.quit()
