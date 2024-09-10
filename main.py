import pandas as pd
import time
from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URL of the website to scrape
base_url = "https://wholesale.desty.app/category?category_id=C80004000&from=&pageIndex="
total_pages = 100

# Initialize the ChromeOptions
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run headless (without opening a browser window)

# Initialize the ChromeDriver without specifying the executable_path
driver = webdriver.Chrome(options=options)

# Initialize an empty list to store the scraped data
data_list = []

# Function to extract and append data
def extract_data(product):
    for item in product:
        try:
            # Extract brand_name
            brand_name_element = item.find_element(By.XPATH, './/span[@class="wproduct-storeName"]')
            brand_name = brand_name_element.text

            # Extract product_name
            product_name_element = item.find_element(By.XPATH, './/span[@class="wproduct-name"]')
            product_name = product_name_element.text

            # Extract wholesale_price
            wholesale_price_element = item.find_element(By.XPATH, './/span[@class="wproduct-unLock"]')
            wholesale_price = wholesale_price_element.text

            # Extract retail_price
            retail_price_element = item.find_element(By.XPATH, './/span[@class="wproduct-retailPrice"]')
            retail_price = retail_price_element.text

            # Extract area
            area_element = item.find_element(By.XPATH, './/span[@class="wproduct-describe"]')
            area = area_element.text

            data_list.append([brand_name, product_name, wholesale_price, retail_price, area])
        except (NoSuchElementException, StaleElementReferenceException):
            # Handle exceptions and continue
            pass

# Loop through the pages and scrape data
for page in range(1, total_pages + 1):
    url = base_url + str(page)
    driver.get(url)

    # Wait for the page to load completely
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search-product"]')))

    # Scrape all data on the current page
    products = driver.find_elements(By.XPATH, '//a[@class="wproduct-item product_item"]')
    extract_data(products)

    print(f'Completed page {page}')

# Create a DataFrame from the scraped data
columns = ['brand_name', 'product_name', 'wholesale_price', 'retail_price', 'area']
df = pd.DataFrame(data_list, columns=columns)

# Generate the timestamp in the JKT (Jakarta) timezone
jakarta_timezone = pytz.timezone('Asia/Jakarta')
timestamp = datetime.now(jakarta_timezone).strftime('%Y-%m-%d-%H%M')

# Save the results to a CSV file
csv_filename = f'Desty_scrape_{timestamp}.csv'
df.to_csv(csv_filename, index=False)
print(f'Results saved to {csv_filename}')

# Close the browser
driver.quit()