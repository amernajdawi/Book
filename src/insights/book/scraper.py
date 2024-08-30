import random
import time

import requests
from bs4 import BeautifulSoup


def scrape_amazon_reviews(book_title):
    """
    Scrape Amazon reviews for a given book title.

    This function simulates a browser request to Amazon's product review pages,
    extracts review texts, and returns up to 20 reviews.

    Args:
    book_title (str): The title of the book to scrape reviews for.

    Returns:
    list: Up to 20 review texts for the specified book.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    reviews = []
    page = 1

    while len(reviews) < 20 and page <= 5:
        url = f"https://www.amazon.com/product-reviews/{book_title.replace(' ', '+')}/ref=cm_cr_arp_d_paging_btm_next_{page}?pageNumber={page}"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        review_elements = soup.find_all("div", {"data-hook": "review"})

        for review in review_elements:
            review_text = review.find("span", {"data-hook": "review-body"}).text.strip()
            reviews.append(review_text)
            if len(reviews) >= 20:
                break

        page += 1
        time.sleep(random.uniform(1, 3))

    return reviews[:20]


def scrape_book(book_title):
    """
    Scrape reviews for a specific book and format the data.

    This function calls scrape_amazon_reviews to get the reviews,
    then formats the data into a list containing a dictionary with the book title and concatenated reviews.

    Args:
    book_title (str): The title of the book to scrape reviews for.

    Returns:
    list: A list containing a dictionary with the book title and concatenated reviews.
    """
    reviews = scrape_amazon_reviews(book_title)
    return [{"title": book_title, "reviews": " ".join(reviews)}]
