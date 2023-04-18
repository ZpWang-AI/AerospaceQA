from selenium.webdriver.common.by import By
from msedge.selenium_tools import EdgeOptions, Edge


edge_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
edgedriver_location = r"D:\msedgedriver.exe"

options = EdgeOptions()
options.use_chromium = True
options.binary_location = edge_location
driver = Edge(options=options, executable_path=edgedriver_location)


# 打开网页
webpage = r'https://baike.baidu.com/item/%E8%88%AA%E7%A9%BA%E8%88%AA%E5%A4%A9?fromModule=lemma_search-box'
# driver.get("https://www.baidu.com")
driver.get(webpage)


# 查找元素
meta_tags = driver.find_elements(By.XPATH,  '//meta')

# 遍历meta标签，查找其中的'image'和'title'属性
for tag in meta_tags:
    if tag.get_attribute("name") == "image":
        image_url = tag.get_attribute("content")
        print("Image URL:", image_url)
    if tag.get_attribute("property") == "og:title":
        title = tag.get_attribute("content")
        print("Title:", title)

# 关闭浏览器
driver.quit()