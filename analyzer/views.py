# analyzer/views.py

import logging
from requests.exceptions import ReadTimeout, RequestException
from django.http import Http404
from django.shortcuts import render
from .forms import URLForm
from .utils.fevicon import get_favicon
from .utils.pageSpeed import pagespeed_report, final_score




def home_view(request):
    history = request.session.get('history', [])

    # print(f"current history: {history}")

    return render(request, 'analyzer/home.html', {
        'history': history
    })


def analyze_view(request):
    form = URLForm(request.POST)
    if form.is_valid():
        url = form.cleaned_data['url']

        # 1) If URL is already in history, jump straight to that detail
        history = request.session.get('history', [])
        for idx, entry in enumerate(history):
            if entry.get('url') == url:
                # htMX will swap this fragment into #psiFragmentContainer
                return history_detail(request, idx)

        print(f"Analyzing URL: {url}")

        # url favicon
        icon_link = get_favicon(url)

        # report
        try:
            context = pagespeed_report(url, strategy='desktop')
        except ReadTimeout:
            return render(request, 'analyzer/psi_error_fragment.html', {
                'error_message': "Request timed out. Please try again later."
            })
        except KeyError:
            return render(request, 'analyzer/psi_error_fragment.html', {
                'error_message': "Unexpected response format from PageSpeed API. Please Try Again Later"
            })



        # SEO Score & status
        score = final_score(context)

        # Build a new entry
        entry = {
            'url': url,
            'icon_link': icon_link,
            'score': score,
            'context': context,
        }

        # Pull existing history, prepend the new one, trim to 3
        history = request.session.get('history', [])
        history.insert(0, entry)
        request.session['history'] = history[:3]
        return render(request, 'analyzer/psi_fragment.html', entry)


    # On GET or invalid POST, render the home page with the form (and errors)
    history = request.session.get('history', [])
    error_message = "Enter a valid Web Address!"
    return render(request, 'analyzer/psi_error_fragment.html', {'error_message': error_message})



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