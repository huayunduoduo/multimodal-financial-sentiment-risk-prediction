from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
import time

# 配置Selenium
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式
driver = webdriver.Chrome(options=options)

# 替换为实际目标网址
url = 'https://www.stcn.com/article/list/yq.html'  
driver.get(url)

# 等待内容加载
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'no-pr')))

# 新增：滚动加载更多内容
current_count = len(driver.find_elements(By.CLASS_NAME, 'no-pr'))
print(f"初始加载数量: {current_count}")

while True:
    # 滚动到底部
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    try:
        # 等待新内容加载（最多等待5秒）
        wait.until(lambda d: len(d.find_elements(By.CLASS_NAME, 'no-pr')) > current_count)
        current_count = len(driver.find_elements(By.CLASS_NAME, 'no-pr'))
        print(f"加载后数量更新为: {current_count}")
    except TimeoutException:
        print("没有更多内容，停止滚动")
        break

# 提取帖子数据
posts = []
for item in driver.find_elements(By.CLASS_NAME, 'no-pr'):
    try:
        # 标题和链接
        title_elem = item.find_element(By.CSS_SELECTOR, '.tt a')
        title = title_elem.text.strip()
        link = title_elem.get_attribute('href').strip()
        
        # 正文摘要
        content = item.find_element(By.CSS_SELECTOR, '.text.ellipsis-2 a').text.strip()
        
        # 标签处理
        tags = [span.text.strip() for span in item.find_elements(By.CSS_SELECTOR, '.tags span')]
        
        # 来源和时间
        info_spans = item.find_elements(By.CSS_SELECTOR, '.info span')
        source = info_spans[0].text.strip()
        pub_time = info_spans[1].text.strip() if len(info_spans) > 1 else ''
        
        posts.append({
            '标题': title,
            '链接': link,
            '正文': content,
            '标签': ', '.join(tags),
            '来源': source,
            '时间': pub_time
        })
    except Exception as e:
        print(f'Error processing item: {e}')
        continue

# 关闭浏览器
driver.quit()

# 保存到CSV
if posts:
    keys = posts[0].keys()
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    with open(f'stcn舆情动态', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(posts)
    print(f'成功保存{len(posts)}条数据')
else:
    print('未找到有效数据')