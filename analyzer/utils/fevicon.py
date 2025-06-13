# analyzer/utils/fevicon.py

"""
Utility for extracting a site's favicon URL by parsing its HTML.

Functions:
- get_favicon: Fetches the page HTML and locates common favicon link tags, falling back to /favicon.ico.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_favicon(url: str) -> str:
    """
    Retrieve the favicon URL for a given website.

    Args:
        url (str): The base URL of the website (e.g., "https://example.com").

    Returns:
        str: Absolute URL of the favicon.
    """
    # Fetch page HTML
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Search for common favicon <link> tags
    rel_values = ["icon", "shortcut icon", "apple-touch-icon"]
    for rel in rel_values:
        link_tag = soup.find("link", rel=lambda x: x and rel in x.lower())
        if link_tag and link_tag.get("href"):
            href = link_tag["href"]
            # Handle protocol-relative URLs (e.g., //example.com/favicon.ico)
            if href.startswith("//"):
                return "https:" + href
            # Handle root-relative URLs
            if href.startswith("/"):
                return urljoin(url, href)
            # Handle absolute URLs
            return href

    # Fallback: assume /favicon.ico at the site root
    return urljoin(url, "/favicon.ico")


