# Visual Price Comparison Web Application

This Flask web application allows users to compare prices of products detected in images using the **Google Cloud Vision API**.  
Users upload an image, and the app extracts related e-commerce URLs and their corresponding prices.

🚧 **Note:** The app works **perfectly on localhost**. The Render deployment is experimental and may have limitations (session handling & file uploads).  

---

## 🔗 Live Demo

👉 [Deployed Application on Render](https://price-comparison-site-1.onrender.com)  
*(If it doesn’t load correctly, please run locally using the steps below.)*

---

## ✨ Features

- 📸 **Image Upload** – Upload a product image.  
- 🔎 **Google Vision API** – Detects web entities and product matches.  
- 💰 **Price Scraping** – Fetches product prices from Amazon, Flipkart, Myntra, Ajio, Croma, TataCliq, etc.  
- 📊 **Comparison View** – Displays multiple store links with their prices.  
- ⚡ **API-Based Scraping** – Uses [ScraperAPI](https://www.scraperapi.com/) instead of local Selenium/Chrome.  

---

## ⚙️ How It Works

1. **Upload Image** – User uploads a product photo.  
2. **Vision Detection** – Google Vision API finds best-guess labels + matching e-commerce pages.  
3. **Scraper API** – Scrapes those URLs to extract prices.  
4. **Comparison Display** – Results are shown side-by-side for easy comparison.  

---

## 🚀 Installation & Local Usage

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
```

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Create a `.env` file in the root directory:

```plaintext
FLASK_SECRET_KEY=your_secret_key
SCRAPER_API_KEY=your_scraperapi_key
GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json
```

- `google-credentials.json` → Download from Google Cloud Console and place in the project root.  
- `SCRAPER_API_KEY` → [Get a free ScraperAPI key](https://www.scraperapi.com/).  

### 5. Run Locally

```bash
python app.py
```

Then open:  
👉 `http://127.0.0.1:5000`

---

## 🌍 Deployment (Render)

If you want to deploy on Render:

1. Push your code to GitHub.  
2. Create a new **Render Web Service**.  
3. In **Settings → Environment Variables**, add:  
   - `FLASK_SECRET_KEY`  
   - `SCRAPER_API_KEY`  
   - `GOOGLE_APPLICATION_CREDENTIALS` (use Render’s **Secret File** feature).  
4. Set **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
5. Set **Start Command**:
   ```bash
   gunicorn webS:app
   ```

---

## 🛠️ Tech Stack

- **Flask** – Python backend  
- **Google Cloud Vision API** – Product & entity detection  
- **ScraperAPI + BeautifulSoup** – Price scraping  
- **Bootstrap / HTML** – Frontend UI  

---

## ⚠️ Shortcomings of Not Using Selenium

Currently, the application does **not** use Selenium (headless browser automation).  
Instead, it relies on ScraperAPI + BeautifulSoup for lightweight scraping.  

### ✅ Pros:
- Faster and more lightweight.  
- Easier to deploy on cloud platforms (Render, Vercel).  
- No need for Chrome/Chromedriver binaries.  

### ❌ Cons:
- Some prices may be missed if they are **rendered dynamically with JavaScript**.  
- Certain sites with **aggressive anti-bot measures** (like dynamic classes, hidden prices) may block scraping.  
- Selenium would give more **accurate scraping** since it renders the page like a real browser.  

👉 In short: **ScraperAPI = lightweight but limited**, **Selenium = heavier but more accurate**.  

---

## 📌 Roadmap

- [ ] Improve price scraping accuracy  
- [ ] Add more e-commerce sites  
- [ ] Enhance frontend UI  
- [ ] Optional Selenium mode for more reliable scraping  
- [ ] Optimize for cloud deployment (Render/Vercel)  

---

## 🙌 Acknowledgements

- [Flask](https://flask.palletsprojects.com/)  
- [Google Cloud Vision API](https://cloud.google.com/vision)  
- [ScraperAPI](https://www.scraperapi.com/)  
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)  

---

## 📬 Contact

For any questions, reach me at:  
📧 [aman.tshekar@gmail.com](mailto:aman.tshekar@gmail.com)
