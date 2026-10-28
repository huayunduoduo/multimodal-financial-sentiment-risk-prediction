from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import csv
import hashlib

# 创建浏览器驱动并配置
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
driver = webdriver.Chrome(options=options)
driver.set_window_size(1200, 800)  # 设置合适的窗口大小

# 打开目标网址
driver.get('https://www.cls.cn/depth?id=1003')

# 记录已爬取的标题哈希值（用于去重）
scraped_hashes = set()
# 记录页面滚动高度（判断是否加载新内容）
last_scroll_height = driver.execute_script("return document.body.scrollHeight")
# 连续无新数据计数器
no_new_data_count = 0
MAX_NO_NEW_COUNT = 3  # 连续多少次无新数据后停止

# 创建CSV文件保存数据
with open('财联社A股新闻数据.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['阅读数', '标题', '最后更新时间'])

    page_count = 1
    
    while True:
        try:
            print(f"正在爬取第 {page_count} 页...")
            
            # 等待页面内容加载完成
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'subject-interest-image-content-box')]"))
            )

            # 提取所有新闻项容器（以新闻项为单位处理，避免列表错位）
            news_items = driver.find_elements(By.XPATH, "//div[contains(@class, 'subject-interest-image-content-box')]")
            new_data_count = 0

            for item in news_items:
                try:
                    # 提取单条新闻数据
                    title_elem = item.find_element(By.XPATH, ".//a[contains(@class, 'link-hover')]")
                    title = title_elem.text.strip()
                    
                    # 生成标题哈希作为唯一标识
                    title_hash = hashlib.md5(title.encode('utf-8')).hexdigest()
                    
                    # 跳过已爬取的内容
                    if title_hash in scraped_hashes or not title:
                        continue
                    
                    # 提取阅读数和时间
                    read_elem = item.find_element(By.XPATH, ".//div[contains(@class, 'subject-interest-time')]/span[2]")
                    read_count = read_elem.text.replace("阅", "").strip()
                    
                    time_elem = item.find_element(By.XPATH, ".//div[contains(@class, 'subject-interest-time')]/span[1]")
                    update_time = time_elem.text.strip()
                    
                    # 写入数据
                    writer.writerow([read_count, title, update_time])
                    scraped_hashes.add(title_hash)
                    new_data_count += 1
                    
                except StaleElementReferenceException:
                    # 处理元素过时异常
                    continue
                except Exception as e:
                    print(f"提取单条数据出错: {str(e)}")
                    continue
            
            print(f"第 {page_count} 页爬取完成，新增 {new_data_count} 条数据，累计 {len(scraped_hashes)} 条")
            
            # 检查是否有新数据
            if new_data_count == 0:
                no_new_data_count += 1
                print(f"连续 {no_new_data_count} 次无新数据")
                
                # 检查页面高度是否变化，确认是否真的没有新内容
                current_scroll_height = driver.execute_script("return document.body.scrollHeight")
                if current_scroll_height == last_scroll_height:
                    print("页面高度未变化，无新内容加载")
                    no_new_data_count += 1  # 加速触发停止条件
                
                if no_new_data_count >= MAX_NO_NEW_COUNT:
                    print("已获取所有可用数据，结束爬取")
                    break
            else:
                no_new_data_count = 0
                # 更新滚动高度
                last_scroll_height = driver.execute_script("return document.body.scrollHeight")

            # 查找并点击"加载更多"按钮
            try:
                # 先滚动到加载更多按钮可见
                load_more = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'list-more-button')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView();", load_more)
                time.sleep(0.5)  # 等待滚动完成
                
                # 确认按钮可点击后再点击
                load_more = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'list-more-button')]"))
                )
                driver.execute_script("arguments[0].click();", load_more)
                print("点击加载更多按钮")
                
                # 等待新内容加载（通过页面高度变化判断）
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.body.scrollHeight") > last_scroll_height
                )
                
                # 随机等待一段时间，模拟人类行为
                wait_time = 1.5  # 可根据实际情况调整
                time.sleep(wait_time)
                
                page_count += 1
                
            except TimeoutException:
                print("未找到加载更多按钮或页面未更新，可能已到达最后一页")
                break
            except Exception as e:
                print(f"点击加载更多出错: {str(e)}")
                break
                
        except Exception as e:
            print(f"页面处理错误：{str(e)}，尝试继续爬取...")
            time.sleep(3)
            continue

driver.quit()
print(f"爬取完成！共获取 {len(scraped_hashes)} 条不重复数据")
    
