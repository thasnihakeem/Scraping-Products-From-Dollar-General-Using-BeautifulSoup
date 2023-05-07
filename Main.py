import time
import warnings
import pandas as pd
from lxml import etree as etree
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

warnings.filterwarnings('ignore')
driver = webdriver.Chrome(ChromeDriverManager().install())


def extract_content(url):
    driver.get(url)
    page_content = driver.page_source
    product_soup = BeautifulSoup(page_content, 'html.parser')
    dom = etree.HTML(str(product_soup))
    return dom

def extract_product_links(url):
    product_links = []
    page_number = 0
    prev_links_count = -1
    skipped_pages = []
    while True:
        if page_number == 0:
            dom = extract_content(url)
        else:
            dom = extract_content(f"{url}page={page_number}")
        time.sleep(60)
        paths = dom.xpath('//div[@class="dg-product-card row"]/@data-product-detail-page-path')
        time.sleep(60)
        for path in paths:
            link = f"https://www.dollargeneral.com/{path}"
            product_links.append(link)
        links_count = len(product_links)
        print(f"Scraped {links_count} links from page {page_number}")
        next_page_button = dom.xpath(
            '//button[@class="splide__arrow splide__arrow--next"][@data-target="pagination-right-arrow"][@disabled=""]')
        # check whether the button is disabled
        if len(next_page_button) > 0:
            break
        # check whether the button is disabled
        if len(next_page_button) > 0:
            break
        # check if current page has no new links and save its URL
        if links_count == prev_links_count:
            skipped_page_url = f"{url}page={page_number}"
            skipped_pages.append(skipped_page_url)
            print(f"No new links found on page {page_number}. Saving URL: {skipped_page_url}")
        else:
            prev_links_count = links_count
        page_number += 1
    # scrape the skipped pages, if any
    for skipped_page in skipped_pages:
        dom = extract_content(skipped_page)
        time.sleep(60)
        paths = dom.xpath('//div[@class="dg-product-card row"]/@data-product-detail-page-path')
        time.sleep(60)
        for path in paths:
            link = f"https://www.dollargeneral.com/{path}"
            product_links.append(link)
        print(f"Scraped {len(paths)} links from skipped page {skipped_page}")
    print(f"Scraped a total of {len(product_links)} product links")
    return product_links

def get_product_name(dom):
    try:
        Product_name = dom.xpath('//h1[@class="productPickupFullDetail__productName d-none d-md-block"]/text()')[
            0].strip()
    except:
        Product_name = 'Product name is not available'
    return Product_name


def get_product_image_url(dom):
    try:
        image_url = dom.xpath('//figure[@class="carousel__currentImage"]/@style')[0].split("(")[1].split(")")[
            0].replace('"', '')
    except:
        image_url = 'Product image URL is not available'
    return image_url


def get_Star_Rating(dom):
    try:
        star_rating = dom.xpath('//div[@class="pr-snippet-rating-decimal"]/text()')[0]
    except:
        star_rating = "Rating not available"
    return star_rating


def get_review_count(dom):
    try:
        review_count = dom.xpath('//a[@class="pr-snippet-review-count"]/text()')[0].strip()
        review_count = review_count.replace("Reviews", "")
        review_count = review_count.replace('Review', '')
    except:
        review_count = 'Review count is not available'
    return review_count


def get_product_price(dom):
    try:
        price = dom.xpath('//span[@class="product-price"]/text()')[0].strip()
    except:
        price = 'Product price is not available'
    return price


def get_product_description_and_features(dom):
    try:
        product_details = dom.xpath(
            '//div[@id="product__details-section"]/p/text() | //div[@id="product__details-section"]/ul/li/text()')
        product_details = [detail.strip() for detail in product_details]
    except:
        try:
            product_details = dom.xpath('//div[@id="product__details-section"]/text()')
            product_details = [detail.strip() for detail in product_details if detail.strip()]
        except:
            product_details = ['Product details are not available']
    return product_details


def get_product_details(dom):
    try:
        availability = dom.xpath('//span[@class="product__details-available-data"]/text()')[0].strip()
    except:
        availability = 'Availability information is not available'

    try:
        brand = dom.xpath('//span[@class="product__details-brand-data"]/text()')[0].strip()
    except:
        brand = 'Brand information is not available'

    try:
        unit_size = dom.xpath('//span[@class="product__details-unit-size-data"]/text()')[0].strip()
    except:
        unit_size = 'Unit size information is not available'

    try:
        sku = dom.xpath('//span[@class="product__details-sku-id"]/text()')[0].strip()
    except:
        sku = 'SKU information is not available'

    try:
        product_form = dom.xpath('//span[@class="product__details-product-form-data"]/text()')[0].strip()
    except:
        product_form = 'Product form information is not available'

    return availability, brand, unit_size, sku, product_form


def get_stock_status(dom):
    try:
        stock_status = dom.xpath(
            '//p[@class="product__stock-alert product__text-red" and contains(@data-target, "stock-alert-pickup")]/text()')[
            0].strip()
    except:
        try:
            stock_status = dom.xpath('//p[@class="product__stock-alert"]/text()')[0]
        except:
            stock_status = 'Stock status is not available'
    return stock_status


def main():
    url = "https://www.dollargeneral.com/c/seasonal/mothers-day?"
    product_links = extract_product_links(url)

    data = []
    for i, link in enumerate(product_links):
        dom = extract_content(link)
        time.sleep(30)
        product_name = get_product_name(dom)
        image = get_product_image_url(dom)
        rating = get_Star_Rating(dom)
        review_count = get_review_count(dom)
        product_price = get_product_price(dom)
        product_description = get_product_description_and_features(dom)
        product_details = get_product_details(dom)
        stock_status = get_stock_status(dom)

        # Add other product details here
        data.append({'Product Link': link, 'Product Name': product_name, 'image': image, 'Star Rating': rating,
                     'review_count': review_count,
                     'Price': product_price, 'Description': product_description, 'Availability': product_details[0],
                     'Brand': product_details[1],
                     'Unit Size': product_details[2], 'SKU': product_details[3], 'Product Form': product_details[4],
                     'Stock Status': stock_status})

        # Print progress message after processing every 10 product URLs
        if i % 10 == 0 and i > 0:
            print(f"Processed {i} links.")

        # Print completion message after all product URLs have been processed
        if i == len(product_links) - 1:
            print(f"All information for {i + 1} links has been scraped.")

    df = pd.DataFrame(data)
    df.to_csv('product_data.csv')


if __name__ == '__main__':
    main()

