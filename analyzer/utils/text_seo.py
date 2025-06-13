# analyzer/utils/text_seo.py

import requests
from django.conf import settings
from django.http import JsonResponse
import textstat
import logging
from textblob import TextBlob
from analyzer.utils.seo_optimizer import SeoOptimizer

# Initialize logger for this module
logger = logging.getLogger(__name__)


def analyze_seo(text: str) -> dict:
    """
    Analyze SEO features for a block of text: calls TextRazor,
    computes readability, extracts topics, stats, and suggestions.
    """
    # 1) Fetch and parse TextRazor response
    textrazor_json = fetch_textrazor_json(text)
    data_json = textrazor_json.get("response", {})

    # 2) Extract topics and coarse topics (top 5)
    topics = [
        {"label": t["label"], "score": round(t["score"], 2)}
        for t in data_json.get("topics", [])[:5]
    ]
    coarse_topics = [
        {"label": t["label"], "score": round(t["score"], 2)}
        for t in data_json.get("coarseTopics", [])[:5]
    ]

    # 3) Sentiment analysis (fallback to TextBlob)
    sentiment_result = extract_sentiment_comprehensive(text)

    # 4) Text statistics (sentence/word counts, etc)
    stats = analyze_content_structure(data_json)

    # 5) Suggested keywords
    suggestions = extract_keywords(data_json)

    # 6) Readability metrics
    readability = {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "text_standard": textstat.text_standard(text),
        "word_count": stats['words'],
        "sentence_count": stats['sentences'],
        "language": data_json.get("language", "unknown"),
        "language_is_reliable": data_json.get("languageIsReliable", False),
    }

    # 7) Determine main and semantic keywords (top topic and related)
    all_keywords = [t["label"] for t in data_json.get("topics", [])]
    main_keywords = all_keywords[:1]            # Main keyword: top topic
    semantic_keywords = all_keywords[1:4]       # Semantic: next 2–3

    # 8) Analyze optimization opportunities
    optimizer = SeoOptimizer(
        text=text,
        main_keywords=main_keywords,
        semantic_keywords=semantic_keywords,
        readability=readability,
        stats=stats
    )
    opportunities = optimizer.analyze()

    return {
        "suggestions": suggestions,
        "topics": topics,
        "coarse_topics": coarse_topics,
        "readability": readability,
        "sentiment": sentiment_result["sentiment"],
        "sentiment_score": sentiment_result["score"],
        "sentiment_confidence": sentiment_result["confidence"],
        "sentiment_method": sentiment_result["method"],
        "stats": stats,
        "opportunities": opportunities,
    }


def extract_sentiment_comprehensive(text):
    """
    Sentiment analysis fallback using TextBlob polarity.
    """
    blob = TextBlob(text)
    score = blob.sentiment.polarity  # range: -1.0 … +1.0

    if score > 0.1:
        sentiment = "positive"
    elif score < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "score": score,
        "confidence": 0.2,  # Low confidence for fallback
        "method": "keyword_fallback"
    }


def fetch_textrazor_json(text):
    url = "https://api.textrazor.com/"
    headers = {"X-TextRazor-Key": settings.TEXTRAZOR_API_KEY}
    payload = {
        "text": text,
        "extractors": "topics,coarseTopics,sentiment,sentences,language,entities,words"
    }
    try:
        resp = requests.post(url, headers=headers, data=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error(f"TextRazor request failed: {e}")
        return {"response": {}}  # Fallback to empty to avoid crashing later



def analyze_content_structure(data_json):
    """
    Analyze and aggregate text stats: sentences, words, complex words, averages.
    """
    sentences = data_json.get("sentences", [])
    sentence_count = len(sentences)

    word_count = sum(len(s.get("words", [])) for s in sentences)
    words = []
    for s in sentences:
        words += [w['token'] for w in s.get('words', [])]

    # Count complex words: >2 syllables
    complex_word_count = sum(1 for w in words if textstat.syllable_count(w) > 2)
    percent_complex = (complex_word_count / word_count * 100) if word_count else 0
    avg_words_per_sentence = (word_count / sentence_count) if sentence_count else 0
    avg_syllables_per_word = (
        sum(textstat.syllable_count(w) for w in words) / word_count
    ) if word_count else 0

    return {
        "sentences": sentence_count,
        "words": word_count,
        "complex_words": complex_word_count,
        "percent_complex_words": percent_complex,
        "avg_words_per_sentence": avg_words_per_sentence,
        "avg_syllables_per_word": avg_syllables_per_word,
    }


def extract_keywords(data_json, max_keywords=7):
    """
    Extract a set of recommended keywords from topics, entities, and frequent nouns.
    """
    # 1. Top topics by score
    topics = sorted(
        data_json.get("topics", []),
        key=lambda t: -t.get("score", 0)
    )
    topic_labels = [t["label"] for t in topics[:max_keywords] if "label" in t]

    # 2. Top entities (only alphabetic, not numbers)
    entities = [
        e["entityId"]
        for e in data_json.get("entities", [])
        if "entityId" in e and e["entityId"].isalpha()
    ]
    entity_labels = [e for e in entities if e not in topic_labels][:max_keywords]

    # 3. High-frequency nouns (if not enough suggestions)
    word_counts = {}
    for sentence in data_json.get("sentences", []):
        for word in sentence.get("words", []):
            pos = word.get("partOfSpeech", "")
            lemma = word.get("lemma", "")
            if pos.startswith("NN") and lemma.isalpha() and len(lemma) > 2:
                word_counts[lemma.lower()] = word_counts.get(lemma.lower(), 0) + 1

    frequent_nouns = [
        w for w, c in sorted(word_counts.items(), key=lambda x: -x[1])
        if w not in topic_labels and w not in entity_labels
    ][:max_keywords]

    # Merge and deduplicate, return top N
    suggestions = topic_labels + entity_labels + frequent_nouns
    suggestions = list(dict.fromkeys(suggestions))[:max_keywords]
    return suggestions



