import time
import warnings
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

warnings.filterwarnings('ignore')
driver = webdriver.Chrome(ChromeDriverManager().install())

def perform_request_with_retry(driver, url):
    MAX_RETRIES = 5
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        try:
            driver.get(url)
            break
        except:
            retry_count += 1
            if retry_count == MAX_RETRIES:
                raise Exception("Request timed out")
            time.sleep(60)


def extract_product_links(driver, url):
    product_links = []
    page_number = -1  
    prev_links_count = -1
    skipped_pages = []
    while True:
        if page_number <= 0: 
            page_url = url
        else:
            page_url = f"{url}&page={page_number+1}"
        perform_request_with_retry(driver, page_url)
        time.sleep(30)
        paths = driver.find_elements("xpath", '//div[@class="dg-product-card row"]')
        for path in paths:
            link = f"https://www.dollargeneral.com/{path.get_attribute('data-product-detail-page-path')}"
            product_links.append(link)
        links_count = len(product_links)
        print(f"Scraped {links_count} links from page {page_number+1}")
        next_page_button = driver.find_elements("xpath", '//button[@class="splide__arrow splide__arrow--next"][@data-target="pagination-right-arrow"][@disabled=""]')
        if len(next_page_button) > 0:
            break
        if links_count == prev_links_count:
            skipped_page_url = page_url
            skipped_pages.append(skipped_page_url)
            print(f"No new links found on page {page_number+1}. Saving URL: {skipped_page_url}")
        else:
            prev_links_count = links_count
        page_number += 1
    for skipped_page in skipped_pages:
        perform_request_with_retry(driver, skipped_page)
        time.sleep(30)
        paths = driver.find_elements("xpath", '//div[@class="dg-product-card row"]')
        for path in paths:
            link = f"https://www.dollargeneral.com/{path.get_attribute('data-product-detail-page-path')}"
            product_links.append(link)
        print(f"Scraped {len(paths)} links from skipped page {skipped_page}")
    print(f"Scraped a total of {len(product_links)} product links")
    return product_links

def get_product_name():
    try:
        product_name = driver.find_element("xpath",'//h1[@class="productPickupFullDetail__productName d-none d-md-block"]')
        product_name = product_name.text
    except:
        product_name = 'Product name is not available'
    return product_name

def get_image_url():
    try:
        image_url = driver.find_element("xpath","//figure[@class='carousel__currentImage']/img").get_attribute('src')
    except:
        image_url = 'Image URL is not available'
    return image_url

def get_star_rating():
    try:
        rating_string = driver.find_element_by_xpath("//div[contains(@class,'pr-snippet-stars') and @role='img']")
        rating_string = rating_string.get_attribute("aria-label")
        rating = float(rating_string.split()[1])
    except:
        rating = 'Product rating is not available'
    return rating

def get_number_of_reviews():
    try:
        number_of_reviews = driver.find_element("xpath",'//a[@class="pr-snippet-review-count"]')
        number_of_reviews = number_of_reviews.text
        number_of_reviews = number_of_reviews.replace("Reviews", "")
        number_of_reviews = number_of_reviews.replace('Review', '')
    except:
        number_of_reviews = 'Number of Reviews is not available'
    return number_of_reviews

def get_product_price():
    try:
        product_price = driver.find_element("xpath","//div[@class='productPriceQuantity']//span[@class='product-price']").text
    except:
        product_price = 'Product price is not available'
    return product_price

def get_stock_status():
    try:
        stock_info = driver.find_element("xpath","//p[@class='product__stock-alert' and @data-target='stock-alert-pickup']").text
    except:
        try:
            stock_info = driver.find_element("xpath","//p[contains(@class,'product__stock-alert') and contains(@class,'product__text-red')]").text
        except:
            stock_info = 'Stock information is not available'
    return stock_info

def get_product_description_and_features():
    try:
        product_description = driver.find_element("xpath","//div[@id='product__details-section']")
        description_list = product_description.text.split('\n')[1:]
    except:
        try:
            product_description = driver.find_element("xpath",'//div[@id="product__details-section"]')
            description_list = product_description.text.split('\n')
        except:
            description_list = ['Product details are not available']
    return description_list

    return description_list

def get_product_details():
    try:
        details_dict = {}
        show_more_button = driver.find_element_by_xpath("//button[@class='product__details-button' and @data-target='show-more-button']")
        show_more_button.click()
        details_list = driver.find_elements_by_xpath('//div[@class="product__details-data"]/div')
        for detail in details_list:
            detail_name = detail.find_element_by_xpath('p').text
            detail_value = detail.find_element_by_xpath('span').text
            if detail_name != '':
                details_dict[detail_name] = detail_value
    except:
        details_dict = {'Product details': 'Not available'}
        
    brand_description = details_dict.get('Brand Description', 'Brand Description not available')
    unit_size = details_dict.get('Unit Size', 'Unit Size not available')
    sku = details_dict.get('SKU', 'SKU not available')
    return details_dict, brand_description, unit_size, sku

def main():
    url = "https://www.dollargeneral.com/c/seasonal/mothers-day?"
    product_links = extract_product_links(driver, url)

    data = []
    for i, link in enumerate(product_links):
        perform_request_with_retry(driver, link)
        time.sleep(60)  
        product_name = get_product_name()
        image = get_image_url()
        rating = get_star_rating()
        review_count = get_number_of_reviews()
        product_price = get_product_price()
        stock_status = get_stock_status()
        product_description = get_product_description_and_features()
        product_details, brand_description, unit_size, sku = get_product_details()


        data.append({'Product Link': link, 'Product Name': product_name, 'image': image, 'Star Rating': rating,
                     'review_count': review_count, 'Price': product_price, 'Stock Status': stock_status,
                     'Brand': brand_description, 'Unit_Size': unit_size, 'Sku': sku,
                     'Description': product_description, 'Details': product_details })


        if i % 10 == 0 and i > 0:
            print(f"Processed {i} links.")


        if i == len(product_links) - 1:
            print(f"All information for {i + 1} links has been scraped.")
            
    df = pd.DataFrame(data)
    df.to_csv('product_data.csv')
    print('CSV file has been written successfully.')
    
    driver.close()

if __name__ == '__main__':
    main()


# In[ ]:





# In[ ]:




