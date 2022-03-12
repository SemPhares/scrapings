import time
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# create webdriver object
driver = webdriver.Chrome(executable_path="chromedriver.exe")
# driver = webdriver.Firefox(executable_path='geckodriver.exe')*

#load the page
driver.get("https://data.inpi.fr")

#make the request
req = driver.find_element_by_class_name("search-input")
req.clear()
req.send_keys('Societe generale')
req.submit()

time.sleep(randint(3,6))

# #navigate through the pages
# nexts = driver.find_elements(By.XPATH, "//a[contains(@class,'mr-3 ')]")
# for next_ in nexts: #range(len(nexts)-1):
#     next_.click()

#get the link on the page
elems = driver.find_elements(By.XPATH, "//a[contains(@class,'not-link')]")
links = list(set([elem.get_attribute('href') for elem in elems]))
# len(links)

#get the information for each link
for i in range(0,len(links)):
    driver.get(links[i])
    download_button = driver.find_element_by_xpath("//div[contains(@class,'col-2')][@title='Télécharger']")
    download_button.click()
    driver.implicitly_wait(randint(5,10))


driver.close()