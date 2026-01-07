import requests
from bs4 import BeautifulSoup
import html
import re

URL = "https://books.toscrape.com/catalogue/category/books/science_22/index.html"
OUTFILE = "books.txt"
THRESHOLD = 20.0  # price threshold for rejection
print("threshold:", THRESHOLD)

def fetch_page(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_books(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")
    books = []

    for article in soup.select("article.product_pod"):
        # Title
        a = article.find("h3").find("a")
        title = a.get("title") or a.get_text(strip=True)

        # Price
        price_tag = article.select_one("p.price_color")
        price_text = price_tag.get_text(strip=True) if price_tag else ""
        price = 0.0
        if price_text:
            cleaned = html.unescape(price_text)
            m = re.search(r"[\d\.,]+", cleaned)
            if m:
                num = m.group(0).replace(",", "")
                try:
                    price = float(num)
                except ValueError:
                    price = 0.0
        
        books.append((title, price))
    return books

def save_books_to_file(books, threshold):
    with open(OUTFILE, "w", encoding="utf-8") as f:
        for title, price in books:
            status = "Accepted" if price <= threshold else "Rejected"
            f.write(f"{status:9} | £{price:7.2f} | {title}\n")

def print_summary(books, threshold):
    total_cost = sum(price for _, price in books)
    accepted = sum(1 for _, price in books if price <= threshold)
    rejected = len(books) - accepted

    print(f"\nSummary:")
    print(f"Total books : {len(books)}")
    print(f"Total cost  : £{total_cost:.2f}")
    print(f"Accepted    : {accepted}")
    print(f"Rejected    : {rejected}")

def main():
    try:
        html_content = fetch_page(URL)
        books = parse_books(html_content)
        save_books_to_file(books, THRESHOLD)
        print(f"\nBooks saved to '{OUTFILE}'")
        print_summary(books, THRESHOLD)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
