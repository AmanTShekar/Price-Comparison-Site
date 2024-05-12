from flask import Flask, request, jsonify, render_template, session
import os
from google.cloud import vision
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google.cloud.vision_v1 import types

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

UPLOAD_FOLDER = 'uploads'

ECOMMERCE_SITES = {
    'www.amazon.in': '//span[@class="a-price-whole"]',
    'www.myntra.com': '//span[@class="pdp-product-price"]',
    'www.flipkart.com': '//div[contains(@class, "_30jeq3") and contains(@class, "_16Jk6d")]',
    'www.croma.com': '//span[@class="amount"]',
    'www.tatacliq.com': '//span[@class="salePrice"]',
    'www.ajio.com': '//span[@class="prod-sp"]'
}

class WebDriverManager:
    def __init__(self):
        self.driver = None

    def get_driver(self):
        if not self.driver:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

web_driver_manager = WebDriverManager()

def scrape_price(url, xpath):
    driver = web_driver_manager.get_driver()
    try:
        driver.get(url)
        price_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        price = price_element.text.strip()
        return price
    except Exception as e:
        return f"Error: {e}"

def scrape_flipkart_price(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    possible_class_names = ["_1vC4OE _3qQ9m1", "_3auQ3N _1POkHg", "_30jeq3 _16Jk6d", "_3qQ9m1","Nx9bqj CxhGGd","yRaY8j A6+E6v"]
    for class_name in possible_class_names:
        price_element = soup.find('div', class_=class_name)
        if price_element:
            price = price_element.text.strip()
            return price
    return "Price not found"

def extract_domain(url):
    parsed_uri = urlparse(url)
    return parsed_uri.netloc

def detect_web(image_content):
    client = vision.ImageAnnotatorClient()

    image = vision.Image(content=image_content)

    response = client.web_detection(image=image)
    annotations = response.web_detection

    results = {'urls_with_prices': []}

    if annotations.best_guess_labels:
        results['best_guess_labels'] = [label.label for label in annotations.best_guess_labels]

    if annotations.pages_with_matching_images:
        for page in annotations.pages_with_matching_images:
            if extract_domain(page.url) in ECOMMERCE_SITES:
                price_xpath = ECOMMERCE_SITES.get(extract_domain(page.url))
                if extract_domain(page.url) == 'www.flipkart.com':
                    price = scrape_flipkart_price(page.url)
                else:
                    price = scrape_price(page.url, price_xpath)
                url_string = str(page.url)
                price_string = str(price)
                results['urls_with_prices'].append({'url': url_string, 'price': price_string})

    if response.error.message:
        raise Exception(response.error.message)

    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400

    try:
        with file as f:
            file_bytes = f.read()

        results = detect_web(file_bytes)

        session['results'] = results

        urls_with_prices = results.get('urls_with_prices', [])
        urls = [item['url'] for item in urls_with_prices]
        prices = [item['price'] for item in urls_with_prices]

        return jsonify({'signal': 'search_complete'}), 200
    except Exception as e:
        return jsonify({'signal': 'processing_error', 'location': '/compare.html'}), 500

@app.route('/compare.html', methods=['GET'])
def compare():
    if 'results' not in session:
        return "No data found"

    results = session['results']
    
    urls_with_prices = results.get('urls_with_prices', [])
    urls = [item['url'] for item in urls_with_prices]
    prices = [item['price'] for item in urls_with_prices]

    return render_template('compare.html', urls=urls, prices=prices)

if __name__ == '__main__':
    app.run(debug=False, port=int(os.environ.get('PORT', 5000)))
