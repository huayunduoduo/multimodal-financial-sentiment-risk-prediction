from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import csv
import random

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
# chrome_options.add_argument("--headless")  # 如果需要无头模式可以取消注释

driver = webdriver.Chrome(options=chrome_options)

class ImmediateSaveCSV:
    def __init__(self, filename):
        self.file = open(filename, 'w', newline='', encoding='utf-8-sig')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['标题', '内容', '最后更新时间'])
        self.flush()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
    
    def flush(self):
        self.file.flush()

try:
    driver.get('https://xueqiu.com/S/SH000300')
    time.sleep(3)

    # 处理可能的弹窗
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal-close"))
        ).click()
        print("已关闭弹窗")
    except:
        pass

    with ImmediateSaveCSV('雪球网沪深300清洗数据.csv') as saver:
        last_first_item = None
        page_count = 1

        while True:
            try:
                # 等待新内容稳定加载
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article.timeline__item"))
                )
                
                # 获取当前页首条元素的ID作为标识
                current_first_item = driver.find_elements(By.CSS_SELECTOR, "article.timeline__item")[0].get_attribute("id")
                
                # 检测是否重复
                if current_first_item == last_first_item:
                    print("检测到重复数据，终止采集")
                    break
                last_first_item = current_first_item

                posts = driver.find_elements(By.CSS_SELECTOR, "article.timeline__item")
                print(f"第{page_count}页共找到 {len(posts)} 个帖子")

                # 采集数据
                collected_data = []
                for post in posts:
                    try:
                        # 改进后的标题定位方式
                        title_element = post.find_elements(By.CSS_SELECTOR, "h3.timeline__item__title")
                        title = title_element[0].text.strip() if title_element else "无标题"
                        
                        # 内容定位
                        content = post.find_element(By.CSS_SELECTOR, "div.content--description").text.replace('\n', ' ')
                        
                        # 时间定位
                        time_element = post.find_element(By.CSS_SELECTOR, "a.date-and-source")
                        post_time = time_element.text.split('·')[0].strip()
                        
                        collected_data.append([title, content, post_time])
                    except Exception as e:
                        print(f"部分数据采集失败: {str(e)}")
                        continue

                # 批量写入数据
                saver.writer.writerows(collected_data)
                saver.flush()
                print(f"已保存{len(collected_data)}条数据")

                # 改进后的翻页逻辑
                try:
                    next_btn = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.pagination__next:not([disabled])"))
                    )
                    
                    # 使用JavaScript直接点击避免元素遮挡
                    driver.execute_script("arguments[0].click();", next_btn)
                    
                    # 等待新内容加载完成
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "article.timeline__item"))
                    )
                    
                    page_count += 1
                    time.sleep(random.uniform(2, 3))  # 更长的随机等待时间
                    
                except Exception as e:
                    print(f"翻页失败，可能已达最后一页: {str(e)}")
                    break

            except Exception as e:
                print(f"采集终止: {str(e)}")
                break

finally:
    driver.quit()
    print("数据采集完成！")