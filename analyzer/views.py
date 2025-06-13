# analyzer/views.py

"""
analyzer/views.py

This module defines all view functions for the SEO Analyzer app.

Views:
- home_view: Render the homepage with the URL input form and recent search history.
- analyze_view: Handle form submission (HTMX or standard POST), perform SEO analysis via PageSpeed & favicon utilities, manage session history, and render results or errors.
- history_detail: Retrieve and display a past analysis from session history by index.
"""
import requests
import logging
from requests.exceptions import ReadTimeout, RequestException
from django.http import Http404, JsonResponse
from django.shortcuts import render

from .forms import URLForm, TextForm
from .utils.fevicon import get_favicon

from .forms import TextForm
from .utils.insert_keyword import insert_keyword_smart
from .utils.text_seo import *

# Initialize module logger
logger = logging.getLogger(__name__)

def home_view(request):
    """
    Display the homepage with an empty URL form and previous search history.

    Context:
        form (URLForm): Form for entering a URL to analyze.
        history (list): List of recent searches stored in session.
    """
    form = URLForm()
    history = request.session.get('history', [])
    return render(request, 'analyzer/home.html', {
        'text_form': TextForm(),
        'history': history,
    })



# analyzer/views.py


def analyze_text_view(request):
    form    = TextForm(request.POST or None)
    history = request.session.get('text_history', [])

    if not form.is_valid():
        return render(request, 'analyzer/text_fragment.html', {
            'text_form': form,
            'history':   history,
            'error_message': form.errors['content'][0],
        })

    content = form.cleaned_data['content']

    # 1) Call TextRazor
    try:
        raw =analyze_seo(content)
    except requests.RequestException as e:
        return render(request, 'analyzer/text_fragment.html', {
            'text_form':    form,
            'history':      history,
            'error_message': f"TextRazor API error: {e}",
        })

    # 2) Print raw JSON to your console/log for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("TextRazor raw response: %s", raw)

    # 3) For now, just return the raw JSON into the fragment so you can see it
    # return JsonResponse(raw)
    return render(request, 'analyzer/text_fragment.html', {
        'suggestions':raw['suggestions'],
        'opportunities': raw['opportunities'],
        'topics': raw['topics'],
        'coarse_topics': raw['coarse_topics'],
        'readability': raw['readability'],
        "sentiment": raw['sentiment'],
        "stats": raw['stats'],
        'content': content,
        'text_form': TextForm(),  # reset form if you need it
        'history': history,

    })

def insert_keyword_view(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        keyword = request.POST.get("keyword", "")
        # Smart insertion (see below)
        new_text = insert_keyword_smart(text, keyword)
        # Return only the updated textarea HTML
        return JsonResponse({"new_text": new_text})




# def analyze_view(request):
#     """
#     Handle URL analysis requests via HTMX or standard POST:
#
#     - On GET or invalid URL POST: return form fragment with validation error.
#     - If URL exists in session history: return saved detail fragment.
#     - Otherwise, fetch PageSpeed report, handle errors, store result in history,
#       and return full report fragment.
#     """
#     # Bind form to POST data or initialize empty
#     form = URLForm(request.POST or None)
#     history = request.session.get('history', [])
#
#     # If form is invalid (or GET), render fragment with error
#     if not form.is_valid():
#         return render(request, 'analyzer/psi_fragment.html', {
#             'form': form,
#             'history': history,
#             'error_message': form.errors['url'][0],
#         })
#
#     url = form.cleaned_data['url']
#
#     # Short-circuit: URL already analyzed? Show history detail.
#     for idx, entry in enumerate(history):
#         if entry['url'] == url:
#             return history_detail(request, idx)
#
#     logger.info("Analyzing URL: %s", url)
#
#     # Attempt to get PageSpeed data
#     try:
#         report = pagespeed_report(url, strategy='desktop')
#         score = final_score(report)
#         icon = get_favicon(url)
#     except ReadTimeout:
#         error = "PageSpeed API timed out. Please try again later."
#     except KeyError:
#         error = "Received unexpected data from PageSpeed API."
#     except RequestException as e:
#         error = f"Network error ({e.__class__.__name__}). Please retry."
#     else:
#         # On success, prepend to history (keep only newest 3)
#         entry = {'url': url, 'icon_link': icon, 'score': score}
#         history.insert(0, entry)
#         request.session['history'] = history[:3]
#
#         # Render report fragment
#         return render(request, 'analyzer/psi_fragment.html', {
#             'form': form,
#             'history': history,
#             'url': url,
#             'icon_link': icon,
#             'score': score,
#             'context': report,
#         })
#
#     # On error, log and render fragment with error
#     logger.warning("Analysis failed for %s: %s", url, error)
#     return render(request, 'analyzer/psi_fragment.html', {
#         'form': form,
#         'history': history,
#         'error_message': error,
#     })


def history_detail(request, idx):
    """
    Display the full details of a past analysis from session history.

    Args:
        idx (int): Index in the history list.

    """
    history = request.session.get('history', [])
    try:
        entry = history[int(idx)]
    except (IndexError, ValueError):
        raise Http404("No such history item.")

    # Render the same fragment, pre-filled with the saved data
    return render(request, 'analyzer/psi_fragment.html', {
        'form': URLForm(initial={'url': entry['url']}),
        'history': history,
        'url': entry['url'],
        'icon_link': entry['icon_link'],
        'score': entry['score'],
        'context': entry.get('context'),
    })
