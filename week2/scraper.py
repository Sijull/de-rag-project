import requests
from bs4 import BeautifulSoup
import os

# 1. Define target URLs (Using some Airflow docs as example data)
URLS = [
    "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html",
    "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html",
    "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html"
]

OUTPUT_DIR = "data"

def scrape_and_save(urls):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for i, url in enumerate(urls):
        try:
            print(f"Scraping: {url}")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract main content (this selector works for standard sphinx docs, adjust for others)
            # If scraping generic sites, soup.body.get_text() is a rough fallback
            content = soup.find('main') 
            if not content:
                content = soup.body
            
            text = content.get_text(separator='\n', strip=True)
            
            # Save to file
            filename = f"{OUTPUT_DIR}/doc_{i+1}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Source: {url}\n\n")
                f.write(text)
            
            print(f"Saved to {filename}")
            
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

if __name__ == "__main__":
    scrape_and_save(URLS)