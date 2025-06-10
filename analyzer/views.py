import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .utils.pageSpeed import fetch_pagespeed_report, pagespeed_report, final_score

from .utils.fevicon import get_favicon


import urllib
from bs4 import BeautifulSoup



# Create your views here.

def home_view(request):
    return render(request,'analyzer/home.html')



def analyze_view(request):
    url = request.POST.get('url')
    print(f"Analyzing URL: {url}")

    # url favicon
    icon_link = get_favicon(url)

    #report
    context = pagespeed_report(url,strategy='desktop')

    # SEO Score
    score = final_score(context)

    return render(request, 'analyzer/psi_fragment.html', {'context': context,'url': url, 'icon_link': icon_link, 'score': score})







# def analyze_view(request):
#     url = request.POST.get('url')
#     print(f"Analyzing URL: {url}")
#
#     # url favicon
#     icon_link = get_favicon(url)
#     # print(f"Icon link found: {icon_link}")
#
#     #report
#     result = fetch_pagespeed_report(url, strategy='desktop')
#     audits = result.get('audits', {})
#     report = {}
#     for key in ['first-contentful-paint', 'speed-index', 'interactive']:
#         if key in audits:
#             a = audits[key]
#             report[key] = {
#                 'description': a.get('description'),
#                 'displayValue': a.get('displayValue'),
#                 'score': a.get('score'),
#             }
#
#     return render(request, 'analyzer/psi_fragment.html', {'report': report, 'icon_link': icon_link})
