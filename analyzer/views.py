from datetime import timezone

import requests
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render
from .utils.pageSpeed import fetch_pagespeed_report, pagespeed_report, final_score

from .utils.fevicon import get_favicon





# Create your views here.

def home_view(request):
    history = request.session.get('history', [])

    # print(f"current history: {history}")

    return render(request, 'analyzer/home.html', {
        'history': history
    })




def analyze_view(request):
    url = request.POST.get('url')
    print(f"Analyzing URL: {url}")

    # url favicon
    icon_link = get_favicon(url)

    #report
    context = pagespeed_report(url,strategy='desktop')

    # SEO Score
    score = final_score(context)

    # Build a new entry
    entry = {
        'url':       url,
        'icon_link': icon_link,
        'score':     score,
        'context':   context,   # this can be any JSON-serializable object
    }

    # Pull existing history, prepend the new one, trim to 3
    history = request.session.get('history', [])
    history.insert(0, entry)
    request.session['history'] = history[:3]

    # print(f"History updated: {request.session['history']}")

    return render(request, 'analyzer/psi_fragment.html', {'context': context,'url': url, 'icon_link': icon_link, 'score': score})



def history_detail(request, idx):

    print(f"Fetching history detail for index: {idx}")
    history = request.session.get('history', [])
    try:
        entry = history[int(idx)]
    except (IndexError, ValueError):
        raise Http404("No such history item.")

    # entry has keys: url, icon_link, score, context
    return render(request, 'analyzer/psi_fragment.html', {
        'context':    entry['context'],
        'url':        entry['url'],
        'icon_link':  entry['icon_link'],
        'score':      entry['score'],
    })