# analyzer/urls.py

"""
URL configuration for the analyzer app.

Routes:
- Home view: renders the input form and shows recent search history.
- Analyze: processes HTMX POST or standard submission to generate/report SEO analysis.
- History detail: retrieves a past analysis by its index in session history.
"""

from django.urls import path
from .views import *

urlpatterns = [
    path('', home_view, name='analyzer'),
    # path('analyze/', analyze_view, name='analyze'),
    path('history/<int:idx>/', history_detail, name='history_detail'),
    path('analyze-text/', analyze_text_view, name='analyze_text'),

]
