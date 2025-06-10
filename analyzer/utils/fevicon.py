# analyzer/utils/fevicon.py


import requests
from bs4 import BeautifulSoup


def get_favicon(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Try common favicon rel types
    rel_values = ["icon", "shortcut icon", "apple-touch-icon"]

    for rel in rel_values:
        link_tag = soup.find("link", rel=lambda x: x and rel in x.lower())
        if link_tag and link_tag.get("href"):
            href = link_tag["href"]
            # Make it a full URL if it's relative
            if href.startswith("//"):
                return "https:" + href
            elif href.startswith("/"):
                from urllib.parse import urljoin
                return urljoin(url, href)
            else:
                return href

    # Fallback to default favicon location
    from urllib.parse import urljoin
    return urljoin(url, "/favicon.ico")


# Example usage:
icon_link = get_favicon("https://example.com")
print(icon_link)
