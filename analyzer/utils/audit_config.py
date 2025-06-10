# analyzer/utils/audit_config.py

SEO_AUDIT_CONFIG = {
    "title": {
        "audit_key": "document-title",
        "title_map": {
            "Document has a `<title>` element": ("SEO Title is present", 1),
            "default": ("We couldn't find SEO Title", 0),
        }
    },
    "meta_description": {
        "audit_key": "meta-description",
        "title_map": {
            "Document has a meta description": ("Meta description is present", 1),
            "default": ("We couldn't find a meta description", 0),
        }
    },
    "image_alt": {
        "audit_key": "image-alt",
        "custom": lambda audit: (
            ("All images have alt attributes", 1)
            if audit.get("scoreDisplayMode") != "notApplicable"
            else ("Missing alt attributes for images", 0)
        )
    },
    "internal_links": {
        "audit_key": "crawlable-anchors",
        "title_map": {
            "Links are crawlable": ("Links are crawlable", 1),
            "default": ("Too few internal links or uncrawlable links", 0),
        }
    },
    "canonical": {
        "audit_key": "canonical",
        "score": {
            1: ("Canonical tag is present", 1),
            "default": ("No canonical link tag found on the page", 0),
        }
    },
    "noindex": {
        "audit_key": "is-crawlable",
        "score": {
            1: ("The page does not contain any noindex header or meta tag", 1),
            "default": ("Page contains a noindex directive", 0),
        }
    },
    "robots_txt": {
        "audit_key": "robots-txt",
        "score": {
            1: ("The site has a robots.txt file", 1),
            "default": ("The site does not have a valid robots.txt file", 0),
        }
    },
    "structured_data": {
        "audit_key": "structured-data",
        "custom": lambda audit: (
            ("No Schema.org data was found on your page", 0)
            if audit.get("score") is None
            else ("Schema.org data is present and valid", 1)
        )
    },
    "js_minified": {
        "audit_key": "unminified-javascript",
        "score": {
            1: ("All JavaScript files appear to be minified", 1),
            "default": ("Some JavaScript files are not minified or audit not applicable", 0),
        }
    },
    "css_minified": {
        "audit_key": "unminified-css",
        "score": {
            1: ("All CSS files appear to be minified", 1),
            "default": ("Some CSS files are not minified or audit not applicable", 0),
        }
    },
    "server_response_time": {
        "audit_key": "server-response-time",
        "score": {
            1: ("The response time is under 0.2 seconds", 1),
            "default": ("The server response time is slow or not available", 0),
        }
    },
    "https_enabled": {
        "external": True,
        "custom": lambda url: (
            ("The site is using a secure transfer protocol (HTTPS)", 1)
            if url.startswith("https://")
            else ("The site is not using HTTPS", 0)
        )
    },
    "link_text": {
        "audit_key": "link-text",
        "score": {
            1: ("Links have descriptive text", 1),
            "default": ("Some links may lack descriptive text", 0),
        }
    },
    "hreflang": {
        "audit_key": "hreflang",
        "score": {
            1: ("Document has a valid hreflang", 1),
            "default": ("Document does not use valid hreflang", 0),
        }
    },
}
