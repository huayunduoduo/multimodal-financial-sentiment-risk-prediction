from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import time

# 常量定义 - 高速模式配置（启用JavaScript）
BASE_URL = 'https://guba.eastmoney.com/list,gssz102021'
START_PAGE =3240 # 起始页码
END_PAGE = 3930 # 结束页码
WAIT_TIMEOUT = 3  # 元素等待超时时间(秒)
MINIMAL_DELAY = 0.5  # 最小延迟时间(秒)

# XPath表达式常量
READ_XPATH = '//td//div[@class="read"]'
REPLY_XPATH = '//td//div[@class="reply"]'
TITLE_XPATH = '//td//div[@class="title"]/a'
AUTHOR_XPATH = '//td//div[@class="author cl"]/a'
UPDATE_XPATH = '//td//div[@class="update mod_time"]'
CLOSE_BUTTON_XPATH = '//img[contains(@src, "ic_close.png")]'
NEXT_PAGE_BUTTON = '//a[contains(@class, "nextp")]'

def get_page_url(page_num):
    """根据页码生成对应的URL"""
    if page_num == 1:
        return f"{BASE_URL}.html"
    return f"{BASE_URL}_{page_num}.html"

def main():
    # 配置Chrome选项以提高速度（不禁用JavaScript）
    chrome_options = webdriver.ChromeOptions()
    # 禁用图片加载，大幅提高页面加载速度
    prefs = {
        "profile.managed_default_content_settings.images": 2,  # 禁用图片
        "profile.managed_default_content_settings.stylesheets": 1,  # 不禁用CSS
        "profile.managed_default_content_settings.javascript": 1  # 启用JavaScript
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # 无头模式（无界面运行），提高速度但保持JavaScript可用
    chrome_options.add_argument("--headless=new")
    # 禁用GPU加速
    chrome_options.add_argument("--disable-gpu")
    # 禁用不必要的插件
    chrome_options.add_argument("--disable-plugins")
    # 禁用扩展
    chrome_options.add_argument("--disable-extensions")
    # 禁用弹窗拦截
    chrome_options.add_argument("--disable-popup-blocking")
    # 禁用默认应用
    chrome_options.add_argument("--no-default-browser-check")
    # 忽略证书错误
    chrome_options.add_argument("--ignore-certificate-errors")
    # 禁用自动化控制特征
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # 创建浏览器驱动
    driver = webdriver.Chrome(options=chrome_options)
    # 设置页面加载超时时间
    driver.set_page_load_timeout(5)
    # 最大化窗口（避免响应式布局问题）
    driver.maximize_window()
    
    try:
        with open('股市实战吧.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['阅读数', '评论数', '标题', '作者', '最后更新时间'])
            
            for page_num in range(START_PAGE, END_PAGE + 1):
                try:
                    print(f"爬取第 {page_num} 页...")
                    
                    # 直接访问指定页码
                    page_url = get_page_url(page_num)
                    driver.get(page_url)
                    
                    # 快速等待关键元素出现
                    WebDriverWait(driver, WAIT_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, READ_XPATH))
                    )
                    
                    # 快速关闭广告（如果存在）
                    try:
                        close_button = WebDriverWait(driver, 1).until(
                            EC.element_to_be_clickable((By.XPATH, CLOSE_BUTTON_XPATH))
                        )
                        close_button.click()
                    except:
                        pass  # 不等待广告，直接继续
                    
                    # 批量提取元素
                    read_elements = driver.find_elements(By.XPATH, READ_XPATH)
                    reply_elements = driver.find_elements(By.XPATH, REPLY_XPATH)
                    title_elements = driver.find_elements(By.XPATH, TITLE_XPATH)
                    author_elements = driver.find_elements(By.XPATH, AUTHOR_XPATH)
                    update_elements = driver.find_elements(By.XPATH, UPDATE_XPATH)
                    
                    # 写入数据（使用更高效的方式）
                    data = []
                    for i in range(len(read_elements)):
                        try:
                            data.append([
                                read_elements[i].text.strip(),
                                reply_elements[i].text.strip() if i < len(reply_elements) else '',
                                title_elements[i].get_attribute('title').strip() if i < len(title_elements) else '',
                                author_elements[i].text.strip() if i < len(author_elements) else '',
                                update_elements[i].text.strip() if i < len(update_elements) else ''
                            ])
                        except:
                            continue  # 出错不处理，继续下一条
                    
                    # 一次性写入所有数据，减少I/O操作
                    writer.writerows(data)
                    
                    # 极短延迟，几乎不等待
                    if page_num < END_PAGE:
                        time.sleep(MINIMAL_DELAY)
                    
                except TimeoutException:
                    print(f"第 {page_num} 页超时，跳过...")
                    continue
                except Exception as e:
                    print(f"第 {page_num} 页出错: {str(e)[:30]}...")
                    continue
                
        print(f"已完成 {START_PAGE} 到 {END_PAGE} 页的高速爬取")
                
    except Exception as e:
        print(f"程序错误: {e}")
    finally:
        driver.quit()
        print("爬取结束")

if __name__ == "__main__":
    main()
    