# analyzer/utils/text_seo.py

import requests
from django.conf import settings
from django.http import JsonResponse
import textstat
import logging
from textblob import TextBlob
from analyzer.utils.seo_optimizer import SeoOptimizer


logger = logging.getLogger(__name__)


def analyze_seo(text: str) -> dict:
    """
    Given a block of text, call TextRazor, compute readability, and extract topics & sentiment.
    """
    # 1) Fetch the full TextRazor response
    textrazor_json = fetch_textrazor_json(text)
    data_json = textrazor_json.get("response", {})



    # 2) Primary topics (top 5)
    topics = [
        {"label": t["label"], "score": round(t["score"], 2)}
        for t in data_json.get("topics", [])[:5]
    ]

    # 3) Coarse topics (top 5)
    coarse_topics = [
        {"label": t["label"], "score": round(t["score"], 2)}
        for t in data_json.get("coarseTopics", [])[:5]
    ]

    # 4) Enhanced Sentiment analysis with multiple fallback methods
    sentiment_result = extract_sentiment_comprehensive(text)

    # 5) Sentence & word counts (for completeness)

    stats = analyze_content_structure(data_json)

    # keyword suggestions

    suggestions = extract_keywords(data_json)

#

    # 6) Readability via textstat
    readability = {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "text_standard": textstat.text_standard(text),
        "word_count": stats['words'],
        "sentence_count": stats['sentences'],
        "language": data_json.get("language", "unknown"),
        "language_is_reliable": data_json.get("languageIsReliable", False),
    }

    all_keywords = [t["label"] for t in data_json.get("topics", [])]
    main_keywords = all_keywords[:1]  # Top topic as main keyword
    semantic_keywords = all_keywords[1:4]  # Next 2–3 as related

    # optimization
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
        'opportunities': opportunities,

    }


def extract_sentiment_comprehensive(text):
    """
    Extract sentiment
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
        "confidence": 0.2,  # Low confidence for keyword method
        "method": "keyword_fallback"
    }


def fetch_textrazor_json(text):
    url = "https://api.textrazor.com/"
    headers = {"X-TextRazor-Key": settings.TEXTRAZOR_API_KEY}
    payload = {
        "text": text,
        "extractors": "topics,coarseTopics,sentiment,sentences,language,entities,words"
    }
    resp = requests.post(url, headers=headers, data=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()

def analyze_content_structure(data_json):
    # Sentences
    sentences = data_json.get("sentences", [])
    sentence_count = len(sentences)

    # Words
    word_count = sum(len(s.get("words", [])) for s in sentences)
    words = []
    for s in sentences:
        words += [w['token'] for w in s.get('words', [])]

    # Complex words (syllable count > 2)
    complex_word_count = sum(1 for w in words if textstat.syllable_count(w) > 2)
    percent_complex = (complex_word_count / word_count * 100) if word_count else 0
    avg_words_per_sentence = (word_count / sentence_count) if sentence_count else 0
    avg_syllables_per_word = (sum(textstat.syllable_count(w) for w in words) / word_count) if word_count else 0

    stats = {
        "sentences": sentence_count,
        "words": word_count,
        "complex_words": complex_word_count,
        "percent_complex_words": percent_complex,
        "avg_words_per_sentence": avg_words_per_sentence,
        "avg_syllables_per_word": avg_syllables_per_word,
    }

    # ... topics, readability, etc. as before

    return stats

def extract_keywords(data_json, max_keywords=7):
    # 1. Top topics by score
    topics = sorted(
        data_json.get("topics", []),
        key=lambda t: -t.get("score", 0)
    )
    topic_labels = [t["label"] for t in topics[:max_keywords] if "label" in t]

    # 2. Top entities (avoid numbers)
    entities = [
        e["entityId"]
        for e in data_json.get("entities", [])
        if "entityId" in e and e["entityId"].isalpha()
    ]
    # Take only new ones not already in topic_labels
    entity_labels = [e for e in entities if e not in topic_labels][:max_keywords]

    # 3. High-frequency nouns (if still less than max_keywords)
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

    # Merge and deduplicate
    suggestions = topic_labels + entity_labels + frequent_nouns
    # Limit to max_keywords
    suggestions = list(dict.fromkeys(suggestions))[:max_keywords]

    return suggestions

def seo_optimization_opportunities(text, main_keywords, semantic_keywords, readability, stats):
    opps = []

    # Keyword density
    for keyword in main_keywords:
        count, density = keyword_density(text, keyword, stats['words'])
        if count == 0:
            opps.append(f"Include your main keyword '{keyword}' at least once.")
        elif density < 1:
            opps.append(f"Increase keyword '{keyword}' usage (current density: {density}%).")

    # Semantic keywords
    missing_sem = missing_semantic_keywords(text, semantic_keywords)
    if missing_sem:
        opps.append(f"Consider including related terms: {', '.join(missing_sem)}.")

    # Long sentences
    long_sents = long_sentences(text)
    if long_sents:
        opps.append(f"{len(long_sents)} sentence(s) are too long. Try splitting them.")

    # Large paragraphs
    large_paras = large_paragraphs(text)
    if large_paras:
        opps.append(f"Break up paragraphs with more than 80 words for easier reading.")

    # Power words
    if not POWER_WORDS.intersection(set(text.lower().split())):
        opps.append("Add engaging 'power words' like: best, easy, secret, etc.")

    # Passive voice
    passive = passive_voice_sentences(text)
    if len(passive) > len(TextBlob(text).sentences) * 0.3:
        opps.append("Reduce passive voice. Rewrite sentences to be more direct.")

    # Reading grade
    if readability["flesch_kincaid_grade"] > 10:
        opps.append("Lower the reading grade for a broader audience.")

    # Word count
    if stats["words"] < 300:
        opps.append("Increase content length to at least 300 words for SEO.")

    # Conclusion
    if not has_conclusion(text):
        opps.append("Add a short summary or conclusion at the end.")

    return opps

