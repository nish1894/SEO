# analyzer/urls.py

"""
URL configuration for the analyzer app.

Routes:
- Home view: renders the input form and shows recent search history.
- Analyze: processes HTMX POST or standard submission to generate/report SEO analysis.
- Insert keyword: handles inserting a recommended keyword into text.
"""

from django.urls import path
from .views import *

urlpatterns = [
    # Home page: main analyzer form
    path('', home_view, name='analyzer'),

    # Analyze submitted text (HTMX or normal POST)
    path('analyze-text/', analyze_text_view, name='analyze_text'),

    # Insert a recommended keyword into user text (AJAX/HTMX)
    path('insert-keyword/', insert_keyword_view, name='insert_keyword'),
]
