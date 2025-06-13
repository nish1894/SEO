"""
analyzer/utils/pagespeed.py

Utility functions for querying Google PageSpeed Insights API and transforming its output into a simple SEO context.

Functions:
- pagespeed_report: Fetch and parse SEO-related audits from PageSpeed API into a labeled context dict.
- fetch_pagespeed_report: Perform the raw HTTP GET to the PSI endpoint and return the lighthouseResult.
- final_score: Compute an overall SEO score and status label based on audit results.
- get_status_label: Map a numeric score to a human-readable status.
"""
import requests
from django.conf import settings


def pagespeed_report(url: str, strategy: str = "mobile") -> dict:
    """
    Generate a simplified SEO context from the PageSpeed Insights API response.

    Args:
        url (str): The webpage URL to analyze.
        strategy (str): 'desktop' or 'mobile' form factor for the analysis.

    Returns:
        dict: A mapping of SEO audit keys to a [message, pass_flag] pair.
    """
    # Fetch raw PageSpeed audits dict
    data_json = fetch_pagespeed_report(url, strategy).get('audits', {})

    context = {}

    # 1. Content & Metadata
    # --------------------------------------------------
    # SEO Title presence
    title_audit = data_json.get('document-title', {})
    if title_audit.get('title') == "Document has a `<title>` element":
        context['title'] = ["SEO Title is present", 1]
    else:
        context['title'] = ["We couldn't find SEO Title", 0]

    # Meta Description presence
    meta_desc = data_json.get('meta-description', {})
    if meta_desc.get('title') == "Document has a meta description":
        context['meta_description'] = ["Meta description is present", 1]
    else:
        context['meta_description'] = ["We couldn't find a meta description", 0]

    # Image ALT attribute audit
    image_alt = data_json.get('image-alt', {})
    if image_alt.get('scoreDisplayMode') != "notApplicable":
        context['image_alt'] = ["All images have alt attributes", 1]
    else:
        context['image_alt'] = ["Missing alt attributes for images", 0]

    # Schema.org structured data audit
    schema = data_json.get('structured-data', {})
    if schema.get('score') is None:
        context['structured_data'] = ["No Schema.org data was found on your page", 0]
    else:
        context['structured_data'] = ["Schema.org data is present and valid", 1]

    # Descriptive link text audit
    link_text = data_json.get('link-text', {})
    if link_text.get('score') == 1:
        context['link_text'] = ["Links have descriptive text", 1]
    else:
        context['link_text'] = ["Some links may lack descriptive text", 0]

    # 2. Crawlability & Indexing
    # --------------------------------------------------
    # Internal crawlable links
    internal_links = data_json.get('crawlable-anchors', {})
    if internal_links.get('title') == "Links are crawlable":
        context['internal_links'] = ["Links are crawlable", 1]
    else:
        context['internal_links'] = ["Too few internal links or uncrawlable links", 0]

    # Canonical tag audit
    canonical = data_json.get('canonical', {})
    if canonical.get('score') == 1:
        context['canonical'] = ["Canonical tag is present", 1]
    else:
        context['canonical'] = ["No canonical link tag found on the page", 0]

    # Noindex directive audit
    noindex = data_json.get('is-crawlable', {})
    if noindex.get('score') == 1:
        context['noindex'] = ["The page does not contain any noindex header or meta tag", 1]
    else:
        context['noindex'] = ["Page contains a noindex directive", 0]

    # robots.txt existence
    robots = data_json.get('robots-txt', {})
    if robots.get('score') == 1:
        context['robots_txt'] = ["The site has a robots.txt file", 1]
    else:
        context['robots_txt'] = ["The site does not have a valid robots.txt file", 0]

    # hreflang tags audit
    hreflang = data_json.get('hreflang', {})
    if hreflang.get('score') == 1:
        context['hreflang'] = ["Document has a valid hreflang", 1]
    else:
        context['hreflang'] = ["Document does not use valid hreflang", 0]

    # 3. Technical & Performance
    # --------------------------------------------------
    # Server response time audit
    response_time = data_json.get('server-response-time', {})
    if response_time.get('score') == 1:
        context['server_response_time'] = ["The response time is under 0.2 seconds", 1]
    else:
        context['server_response_time'] = ["The server response time is slow or not available", 0]

    # HTTPS enforcement check
    if url.startswith("https://"):
        context['https_enabled'] = ["The site is using a secure transfer protocol (HTTPS)", 1]
    else:
        context['https_enabled'] = ["The site is not using HTTPS", 0]

    # HTTP status code audit
    status_code = data_json.get('http-status-code', {})
    if status_code.get('score') == 1:
        context['http_status_code'] = ["Page returns a successful HTTP status code", 1]
    else:
        context['http_status_code'] = ["Page does not return a valid HTTP status code", 0]

    # JS minification audit
    js_min = data_json.get('unminified-javascript', {})
    if js_min.get('score') == 1:
        context['js_minified'] = ["All JavaScript files appear to be minified", 1]
    else:
        context['js_minified'] = ["Some JavaScript files are not minified or audit not applicable", 0]

    # CSS minification audit
    css_min = data_json.get('unminified-css', {})
    if css_min.get('score') == 1:
        context['css_minified'] = ["All CSS files appear to be minified", 1]
    else:
        context['css_minified'] = ["Some CSS files are not minified or audit not applicable", 0]

    return context


def fetch_pagespeed_report(url: str, strategy: str = "desktop") -> dict:
    """
    Call the Google PageSpeed Insights API and return the raw lighthouseResult.

    Args:
        url (str): The webpage to analyze.
        strategy (str): The device form factor ('desktop' or 'mobile').

    Returns:
        dict: The `lighthouseResult` portion of the API response (or empty dict on failure).
    """
    params = {
        "url": url,
        "category": "seo",
        "strategy": strategy,
        "key": settings.GOOGLE_PSI_API_KEY,
    }
    resp = requests.get(settings.PSI_ENDPOINT, params=params, timeout=40)
    data = resp.json()
    return data.get("lighthouseResult", {})


def final_score(context: dict) -> dict:
    """
    Compute aggregate SEO scores and visual parameters from the context dict.

    Args:
        context (dict): Mapping of audit keys to [message, pass_flag] pairs.

    Returns:
        dict: Contains counts (all, positives, negatives), percentage score, SVG offset, and status_label.
    """
    count_all = len(context)
    count_positives = sum(value[1] for value in context.values())
    count_negatives = count_all - count_positives
    count_score = int((count_positives / count_all) * 100) if count_all else 0

    # SVG circumference is 2πr ≈ 282.6 for r=45px
    score_offset = 282.6 * (1 - count_score / 100)

    status_label = get_status_label(count_score)

    return {
        'count_all': count_all,
        'count_positives': count_positives,
        'count_negatives': count_negatives,
        'count_score': count_score,
        'score_offset': score_offset,
        'status_label': status_label,
    }


def get_status_label(score: int) -> str:
    """
    Map a numeric score to a human-readable label.

    Args:
        score (int): Percentage score between 0 and 100.

    Returns:
        str: One of 'Poor', 'Average', 'Good', 'Very Good', or 'Excellent'.
    """
    if score < 50:
        return "Poor"
    if score < 60:
        return "Average"
    if score < 70:
        return "Good"
    if score < 80:
        return "Very Good"
    return "Excellent"
