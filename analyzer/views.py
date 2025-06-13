# analyzer/views.py

"""
analyzer/views.py

Defines all view functions for the SEO Analyzer app.

Views:
- home_view: Render homepage with the input form.
- analyze_text_view: Handle text analysis form, invoke TextRazor, display results.
- insert_keyword_view: Smartly insert keyword into text and return the updated result.
"""



from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render

from .forms import  TextForm
from .utils.insert_keyword import insert_keyword_smart
from .utils.text_seo import *

# Initialize module logger
logger = logging.getLogger(__name__)

def home_view(request):
    """
    Render the homepage with the text input form.
    """
    return render(request, 'analyzer/home.html', {
        'text_form': TextForm(),
    })


def analyze_text_view(request):
    """
    Handle POST from the main input form, analyze with TextRazor, and return results fragment.
    """
    form = TextForm(request.POST or None)

    if not form.is_valid():
        # Error: Empty or too short input, send error fragment
        return render(request, 'analyzer/text_fragment_error.html', {
            'error_message': form.errors['content'][0]  # Django will supply a useful message!
        })

    content = form.cleaned_data['content']

    # 1) Call TextRazor and catch any API error
    try:
        raw = analyze_seo(content)
    except requests.Timeout:
        return render(request, 'analyzer/text_fragment_error.html', {
            'error_message': "The SEO analysis service timed out. Please try again."
        })
    except requests.RequestException as e:
        return render(request, 'analyzer/text_fragment_error.html', {
            'error_message': "Could not contact the SEO analysis service. Please try again later."
        })
    except Exception as e:
        return render(request, 'analyzer/text_fragment_error.html', {
            'error_message': "An unexpected error occurred. Please try again."
        })



    # 3) Render the analysis fragment with results
    return render(request, 'analyzer/text_fragment.html', {
        'suggestions': raw['suggestions'],
        'opportunities': raw['opportunities'],
        'topics': raw['topics'],
        'coarse_topics': raw['coarse_topics'],
        'readability': raw['readability'],
        "sentiment": raw['sentiment'],
        "stats": raw['stats'],
        'content': content,
        'text_form': TextForm(),  # reset form
    })


def insert_keyword_view(request):
    """
    POST endpoint: Insert a keyword into the provided text at a smart location.
    Used by the keyword 'plus' button.
    """
    if request.method == "POST":
        keyword = request.POST.get('keyword', '').strip()
        text = request.POST.get('text', '').strip()

        if not keyword or not text:
            return HttpResponse("Missing data", status=400)

        data_json = fetch_textrazor_json(text)
        new_text = insert_keyword_smart(data_json, text, keyword)

        return HttpResponse(new_text, content_type='text/plain')
    return HttpResponse("Error", status=400)
