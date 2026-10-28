from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
import random
import hashlib  # 用于生成标题哈希值
import time

# 初始化浏览器
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-extensions")
# 可以添加无头模式提高速度（注释掉可看到浏览器操作）
# options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)
driver.get('https://stocks.nbd.com.cn')

# 记录已爬取的标题哈希，避免重复
scraped_hashes = set()
# 连续无新数据的次数计数器
no_new_data_count = 0
# 最大连续无新数据次数（超过则认为已爬完）
MAX_NO_NEW_COUNT = 3

with open('nbd_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['阅读数', '标题', '类别', '最后更新时间'])

    page_count = 1
    
    while True:
        try:
            print(f"正在爬取第 {page_count} 页...")
            
            # 等待页面内容加载完成
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'f-title'))
            )

            # 获取页面元素
            read_elements = driver.find_elements(By.XPATH, ".//span[contains(text(),'阅读')]")
            title_elements = driver.find_elements(By.CLASS_NAME, 'f-title')
            category_elements = driver.find_elements(By.CLASS_NAME, 'tag')
            update_elements = driver.find_elements(By.XPATH, "//p[@class='f-source']/span[2]")

            # 确保所有列表长度一致
            min_length = min(len(read_elements), len(title_elements), 
                           len(category_elements), len(update_elements))
            
            new_data_count = 0
            
            for i in range(min_length):
                title = title_elements[i].text.strip()
                # 生成标题的哈希值作为唯一标识
                title_hash = hashlib.md5(title.encode('utf-8')).hexdigest()
                
                # 跳过已爬取的内容
                if title_hash in scraped_hashes:
                    continue
                    
                scraped_hashes.add(title_hash)
                new_data_count += 1
                
                writer.writerow([
                    read_elements[i].text.replace("阅读", ""),
                    title,
                    category_elements[i].text.strip(),
                    update_elements[i].text.split()[0].strip()
                ])
            
            print(f"第 {page_count} 页爬取完成，新增 {new_data_count} 条数据，累计 {len(scraped_hashes)} 条")
            
            # 处理无新数据的情况
            if new_data_count == 0:
                no_new_data_count += 1
                print(f"连续 {no_new_data_count} 次无新数据")
                
                # 如果连续多次无新数据，判断为已爬完所有内容
                if no_new_data_count >= MAX_NO_NEW_COUNT:
                    print("已获取所有可用数据，结束爬取")
                    break
            else:
                # 有新数据则重置计数器
                no_new_data_count = 0

            # 查找并点击"加载更多"按钮
            try:
                load_more = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'加载更多')]"))
                )
                driver.execute_script("arguments[0].click();", load_more)
                
                # 动态调整等待时间，根据新数据量决定
                wait_time = random.uniform(0.8, 1.5) if new_data_count > 0 else random.uniform(1.5, 2.5)
                time.sleep(wait_time)
                
                page_count += 1
                
            except TimeoutException:
                print("未找到加载更多按钮，可能已到达最后一页")
                break
                
        except Exception as e:
            print(f"发生错误：{str(e)}，尝试继续爬取...")
            time.sleep(2)
            continue

driver.quit()
print(f"爬取完成！共获取 {len(scraped_hashes)} 条不重复数据")
    