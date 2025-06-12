# analyzer/utils/pagespeed.py

import requests
from django.conf import settings
from .audit_config import SEO_AUDIT_CONFIG

import json



def pagespeed_report(url: str, strategy: str = "mobile") -> dict:
    context = {}
    data_json = fetch_pagespeed_report(url, strategy)['audits']

    context = {}



    # 1. SEO Title
    title_audit = data_json.get('document-title', {})
    if title_audit.get('title') == "Document has a `<title>` element":
        context['title'] = ["SEO Title is present", 1]
    else:
        context['title'] = ["We couldn't find SEO Title", 0]

    # 2. Meta Description
    meta_desc = data_json.get('meta-description', {})
    if meta_desc.get('title') == "Document has a meta description":
        context['meta_description'] = ["Meta description is present", 1]
    else:
        context['meta_description'] = ["We couldn't find a meta description", 0]

    # 3. Image ALT Attributes
    image_alt = data_json.get('image-alt', {})
    if image_alt.get('scoreDisplayMode') != "notApplicable":
        context['image_alt'] = ["All images have alt attributes", 1]
    else:
        context['image_alt'] = ["Missing alt attributes for images", 0]


    # 4. Crawlable Links (Internal Links)
    internal_links = data_json.get('crawlable-anchors', {})
    if internal_links.get('title') == "Links are crawlable":
        context['internal_links'] = ["Links are crawlable", 1]
    else:
        context['internal_links'] = ["Too few internal links or uncrawlable links", 0]

    # 5. Canonical
    canonical = data_json.get('canonical', {})
    if canonical.get('score') == 1:
        context['canonical'] = ["Canonical tag is present", 1]
    else:
        context['canonical'] = ["No canonical link tag found on the page", 0]

    # 6. Noindex
    noindex = data_json.get('is-crawlable', {})
    if noindex.get('score') == 1:
        context['noindex'] = ["The page does not contain any noindex header or meta tag", 1]
    else:
        context['noindex'] = ["Page contains a noindex directive", 0]

    # 7. robots.txt
    robots = data_json.get('robots-txt', {})
    if robots.get('score') == 1:
        context['robots_txt'] = ["The site has a robots.txt file", 1]
    else:
        context['robots_txt'] = ["The site does not have a valid robots.txt file", 0]

    # 8. Schema.org structured data
    schema = data_json.get('structured-data', {})
    if schema.get('score') is None:
        context['structured_data'] = ["No Schema.org data was found on your page", 0]
    else:
        context['structured_data'] = ["Schema.org data is present and valid", 1]

    # 9. JS Minification
    js_min = data_json.get('unminified-javascript', {})
    if js_min.get('score') == 1:
        context['js_minified'] = ["All JavaScript files appear to be minified", 1]
    else:
        context['js_minified'] = ["Some JavaScript files are not minified or audit not applicable", 0]

    # 10. CSS Minification
    css_min = data_json.get('unminified-css', {})
    if css_min.get('score') == 1:
        context['css_minified'] = ["All CSS files appear to be minified", 1]
    else:
        context['css_minified'] = ["Some CSS files are not minified or audit not applicable", 0]

    # 11. Server Response Time
    response_time = data_json.get('server-response-time', {})
    if response_time.get('score') == 1:
        context['server_response_time'] = ["The response time is under 0.2 seconds", 1]
    else:
        context['server_response_time'] = ["The server response time is slow or not available", 0]

    # 12. HTTPS Check
    if url.startswith("https://"):
        context['https_enabled'] = ["The site is using a secure transfer protocol (HTTPS)", 1]
    else:
        context['https_enabled'] = ["The site is not using HTTPS", 0]

    # 13. Descriptive Link Text
    link_text = data_json.get('link-text', {})
    if link_text.get('score') == 1:
        context['link_text'] = ["Links have descriptive text", 1]
    else:
        context['link_text'] = ["Some links may lack descriptive text", 0]

    # 14. hreflang Tags
    hreflang = data_json.get('hreflang', {})
    if hreflang.get('score') == 1:
        context['hreflang'] = ["Document has a valid hreflang", 1]
    else:
        context['hreflang'] = ["Document does not use valid hreflang", 0]

    # 15. HTTP Status Code
    status_code = data_json.get('http-status-code', {})
    if status_code.get('score') == 1:
        context['http_status_code'] = ["Page returns a successful HTTP status code", 1]
    else:
        context['http_status_code'] = ["Page does not return a valid HTTP status code", 0]



    return context


def fetch_pagespeed_report(url: str, strategy: str = "desktop") -> dict:
    params = {
        "url": url,
        "category": "seo",
        "strategy": strategy,
        "key": settings.GOOGLE_PSI_API_KEY,
    }
    resp = requests.get(settings.PSI_ENDPOINT, params=params, timeout=50)
    data = resp.json()
    # return only the lighthouseResult dict
    return data.get("lighthouseResult", {})

def final_score(context):
    count_all = len(context)
    count_positives = sum(value[1] for value in context.values())
    count_negatives = count_all - count_positives
    count_score = int(count_positives / count_all * 100)

    score_offset = 282.6 * (1 - count_score  / 100) # 282.6 is the circumference of the circle with radius 45px


    score = {'count_all':count_all, 'count_positives':count_positives, 'count_negatives':count_negatives,
             'count_score':count_score, 'score_offset':score_offset}

    return score






