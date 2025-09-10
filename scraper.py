from enum import Enum
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from crud import save_book_information



class WebDriverType(Enum):
    CHROME = 'chrome'
    EDGE = 'edge'
    FIREFOX = 'firefox'
    SAFARI = 'safari'
    INTERNET_EXPLORER = 'internet explorer'


PAGE_URL = "https://books.toscrape.com/index.html"

def perform_scraping(driver_path='/usr/bin/chromedriver', web_driver_type: WebDriverType=WebDriverType.CHROME):
    service = Service(executable_path=driver_path)

    if web_driver_type == WebDriverType.CHROME:
        driver = webdriver.Chrome(service=service)
    elif web_driver_type == WebDriverType.EDGE:
        driver = webdriver.Edge(service=service)
    elif web_driver_type == WebDriverType.FIREFOX:
        driver = webdriver.Firefox(service=service)
    elif web_driver_type == WebDriverType.SAFARI:
        driver = webdriver.Safari(service=service)
    elif web_driver_type == WebDriverType.INTERNET_EXPLORER:
        driver = webdriver.Ie(service=service)
    else:
        raise ValueError(f"Web driver type {web_driver_type} not supported")

    driver.get(PAGE_URL)

    wait = WebDriverWait(driver, 10)
    list_of_categories = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="default"]/div/div/div/aside/div[2]/ul/li/ul')))
    
    # Get all category links
    category_links = list_of_categories.find_elements(By.TAG_NAME, 'a')
    
    # Extract href and text from each link
    categories = []
    for link in category_links:
        href = link.get_attribute('href')
        text = link.text.strip()
        categories.append({'name': text, 'url': href})
        print(f"Category: {text} - URL: {href}")
    
    # Collect all books from all categories
    all_books = []
    for category in categories:
        books = visit_category_page(category['url'], driver)
        all_books.extend(books)
        
    driver.quit()
    
    print(f"\nTotal books collected: {len(all_books)}")
    return all_books


def visit_category_page(link: str, driver):
    driver.get(link)

    wait = WebDriverWait(driver, 10)

    category_name = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="default"]/div/div/div/div/div[1]/h1'))).text
    list_of_books = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="default"]/div/div/div/div/section/div[2]/ol')))
    
    # Get all book links
    book_links = list_of_books.find_elements(By.CSS_SELECTOR, 'h3 a')
    
    urls = []
    for link in book_links:
        book_url = link.get_attribute('href')
        urls.append(book_url)

    for url in urls:
        book_information = visit_book_page(url, driver)
        save_book_information(book_information, category_name)  # Save the information in the database
    
    return urls
    
    


def visit_book_page(link: str, driver):
    driver.get(link)

    wait = WebDriverWait(driver, 10)

    book_upc = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content_inner"]/article/table/tbody/tr[1]/td'))).text

    book_title = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content_inner"]/article/div[1]/div[2]/h1'))).text

    book_price = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content_inner"]/article/table/tbody/tr[3]/td'))).text
    book_price = book_price[1: len(book_price) - 1]

    book_stock = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content_inner"]/article/table/tbody/tr[6]/td'))).text
    book_stock = ''.join(filter(str.isdigit, book_stock))

    book_image_url = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="product_gallery"]/div/div/div/img'))).get_attribute('src')

    book_description = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content_inner"]/article/p'))).text

    book_rating = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content_inner"]/article/div[1]/div[2]/p[3]'))).get_attribute('class')
    if 'One' in book_rating:
        book_rating = 1
    elif 'Two' in book_rating:
        book_rating = 2
    elif 'Three' in book_rating:
        book_rating = 3
    elif 'Four' in book_rating:
        book_rating = 4
    elif 'Five' in book_rating:
        book_rating = 5

    return {
        'upc': book_upc,
        'title': book_title,
        'price': book_price,
        'stock': book_stock,
        'image_url': book_image_url,
        'description': book_description,
        'rating': book_rating
    }