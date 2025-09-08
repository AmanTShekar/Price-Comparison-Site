from flask import Flask, request, render_template, session
import os
import requests
from urllib.parse import urlparse, quote_plus, parse_qs
from bs4 import BeautifulSoup
from google.cloud import vision
import re

app = Flask(__name__)

# Secret key from environment
app.secret_key = os.getenv("FLASK_SECRET_KEY", "local_secret_key")

# ---------- GOOGLE CLOUD VISION ----------
# Path to credentials (Render secret file or local json)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS", "google-credentials.json"
)

# ---------- SCRAPER API ----------
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")

# ---------- ECOMMERCE XPATHS / CLASSES ----------
ECOMMERCE_SITES = {
    'www.amazon.in': '//span[@class="a-price-whole"]',
    'www.myntra.com': '//span[@class="pdp-product-price"]',
    'www.flipkart.com': '//div[contains(@class, "_30jeq3") and contains(@class, "_16Jk6d")]',
    'www.croma.com': '//span[@class="amount"]',
    'www.tatacliq.com': '//span[@class="salePrice"]',
    'www.ajio.com': '//span[@class="prod-sp"]'
}

# ---------- HELPER FUNCTIONS ----------
def clean_price(price_str):
    if not price_str:
        return "N/A"
    price = re.sub(r"[^\d,₹]", "", price_str)
    if not price.startswith("₹"):
        price = "₹" + price
    return price

def scrape_price_with_api(url):
    api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        possible_class_names = [
            "a-price-whole", "pdp-product-price", "_30jeq3 _16Jk6d", "amount",
            "salePrice", "prod-sp", "_1vC4OE _3qQ9m1", "Nx9bqj CxhGGd", "yRaY8j A6+E6v",
            "_25b18c", "_2p6lqe"
        ]
        for class_name in possible_class_names:
            price_element = soup.find(attrs={"class": class_name})
            if price_element:
                return clean_price(price_element.text.strip())
        return "N/A"
    except Exception as e:
        return f"Error: {str(e)}"

def extract_domain(url):
    parsed_uri = urlparse(url)
    return parsed_uri.netloc

def fetch_page(url):
    api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
    resp = requests.get(api_url, timeout=15)
    resp.raise_for_status()
    return resp.text

def detect_web(image_content):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_content)
    response = client.web_detection(image=image)
    annotations = response.web_detection

    results = {"urls_with_prices": []}
    product_label = ""

    if annotations.best_guess_labels:
        product_label = annotations.best_guess_labels[0].label
        results["best_guess_labels"] = [label.label for label in annotations.best_guess_labels]

    flipkart_found = False
    myntra_found = False

    if annotations.pages_with_matching_images:
        for page in annotations.pages_with_matching_images:
            domain = extract_domain(page.url)
            if domain in ECOMMERCE_SITES:
                price = scrape_price_with_api(page.url)
                results["urls_with_prices"].append({"url": page.url, "price": price})
            if "flipkart.com" in domain:
                flipkart_found = True
            if "myntra.com" in domain:
                myntra_found = True

    # Backup Flipkart
    if not flipkart_found and product_label:
        try:
            query = quote_plus(product_label + " site:flipkart.com")
            html = fetch_page(f"https://www.google.com/search?q={query}")
            soup = BeautifulSoup(html, "html.parser")
            link = soup.find("a", href=True)
            if link:
                url = link["href"]
                if url.startswith("/url?q="):
                    url = parse_qs(urlparse(url).query)["q"][0]
                if "flipkart.com" in url:
                    price = scrape_price_with_api(url)
                    results["urls_with_prices"].append({"url": url, "price": price})
        except:
            pass

    # Backup Myntra
    if not myntra_found and product_label:
        try:
            query = quote_plus(product_label + " site:myntra.com")
            html = fetch_page(f"https://www.google.com/search?q={query}")
            soup = BeautifulSoup(html, "html.parser")
            link = soup.find("a", href=True)
            if link:
                url = link["href"]
                if url.startswith("/url?q="):
                    url = parse_qs(urlparse(url).query)["q"][0]
                if "myntra.com" in url:
                    price = scrape_price_with_api(url)
                    results["urls_with_prices"].append({"url": url, "price": price})
        except:
            pass

    if response.error.message:
        raise Exception(response.error.message)

    return results

# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return {"status": "error", "message": "No file uploaded"}, 400

    file = request.files["file"]
    if file.filename == "":
        return {"status": "error", "message": "No image selected"}, 400

    try:
        file_bytes = file.read()
        results = detect_web(file_bytes)
        session["results"] = results
        return {"status": "success"}  # No redirect here
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/compare.html")
def compare():
    if "results" not in session:
        return "No data found. Upload an image first."
    results = session["results"]
    urls_with_prices = results.get("urls_with_prices", [])
    urls = [item["url"] for item in urls_with_prices]
    prices = [item["price"] for item in urls_with_prices]
    return render_template("compare.html", urls=urls, prices=prices)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
