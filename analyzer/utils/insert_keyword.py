# --- Utility for Smart Keyword Insertion into Text ---
#
# Provides natural placement of SEO keywords in user content
# using linguistic hints from Textrazor's output.

def insert_keyword_smart(data_json, text, keyword):
    """
    Suggests and performs a natural, non-repetitive insertion of `keyword` into `text`.

    Args:
        data_json (dict): Textrazor API response with POS/sentence info.
        text (str): The original user text.
        keyword (str): Keyword to insert.

    Returns:
        str: Modified text with the keyword naturally inserted.
    """
    try:
        # Do not duplicate keywords
        if keyword.lower() in text.lower():
            return text

        # Find all possible insertion points using analysis
        insertion_suggestions = find_insertion_points(data_json, text, [keyword])

        if insertion_suggestions:
            # Choose the best option (highest confidence, most natural)
            options = generate_insertion_options(text, insertion_suggestions)
            return options[0]["new_text"]

        # Fallback: insert keyword at the end of the first sentence
        sentences = text.split('.')
        if sentences:
            sentences[0] = sentences[0].strip() + f" {keyword}"
        return '.'.join(sentences)

    except Exception as e:
        return text  # Fallback: return original text unmodified


def generate_insertion_options(original_text, insertion_suggestions):
    """
    For each insertion suggestion, generate candidate texts
    using context-aware templates.

    Returns a list of dicts with new text and metadata.
    """
    options = []
    for suggestion in insertion_suggestions[:5]:  # Top 5 only
        keyword = suggestion['keyword']
        position = suggestion['position']
        context_type = suggestion.get('insertion_type', 'general')
        templates = create_insertion_templates(keyword, context_type)

        for template in templates:
            new_text = (
                original_text[:position] +
                template +
                original_text[position:]
            )
            options.append({
                'keyword': keyword,
                'new_text': new_text,
                'insertion_preview': get_preview(new_text, position, len(template)),
                'confidence': suggestion['confidence'],
                'context': suggestion['context']
            })
    return options


def create_insertion_templates(keyword, context_type):
    """
    Choose context-aware phrase templates for keyword insertion.

    Args:
        keyword (str): The keyword to insert.
        context_type (str): Context, e.g. 'adjective_noun', 'after_preposition'.

    Returns:
        list: List of template strings.
    """
    templates = {
        'adjective_noun': [
            f" {keyword}",
            f" and {keyword}",
            f" {keyword}-related",
        ],
        'after_preposition': [
            f" {keyword}",
            f" the {keyword}",
            f" {keyword} and",
        ],
        'before_conjunction': [
            f"{keyword} ",
            f"including {keyword} ",
            f"{keyword}-focused ",
        ],
        'sentence_start': [
            f"{keyword} ",
            f"The {keyword} ",
            f"Modern {keyword} ",
        ],
        'sentence_end': [
            f" {keyword}",
            f" and {keyword}",
            f" related to {keyword}",
        ]
    }
    return templates.get(context_type, [f" {keyword}"])


def get_preview(text, position, insertion_length):
    """
    Returns a short preview context of the new text around the insertion.

    Args:
        text (str): Full new text.
        position (int): Where the keyword was inserted.
        insertion_length (int): Length of inserted phrase.

    Returns:
        dict: Preview and highlight indices.
    """
    start = max(0, position - 50)
    end = min(len(text), position + insertion_length + 50)
    preview = text[start:end]
    highlight_start = position - start
    highlight_end = highlight_start + insertion_length
    return {
        'preview': preview,
        'highlight_start': highlight_start,
        'highlight_end': highlight_end
    }


def find_insertion_points(data_json, original_text, keywords):
    """
    Use Textrazor response to locate natural, non-intrusive points
    to insert keywords in the text.

    Args:
        data_json (dict): Textrazor API response.
        original_text (str): Full text.
        keywords (list): Keywords to insert.

    Returns:
        list: Ranked list of insertion suggestion dicts.
    """
    sentences = data_json.get("sentences", [])
    insertion_suggestions = []

    for keyword in keywords:
        keyword_lower = keyword.lower()
        for sentence in sentences:
            sentence_text = sentence.get("text", "")
            sentence_start = sentence.get("startingPos", 0)

            # Skip sentences that already contain the keyword
            if keyword_lower in sentence_text.lower():
                continue

            words = sentence.get("words", [])
            insertion_points = find_natural_positions(
                words, sentence_text, keyword, sentence_start
            )
            for point in insertion_points:
                insertion_suggestions.append({
                    'keyword': keyword,
                    'position': point['position'],
                    'context': point['context'],
                    'sentence_text': sentence_text,
                    'confidence': point['confidence'],
                    'insertion_type': point['insertion_type'],
                })
    # Sort suggestions by confidence (descending)
    return sorted(insertion_suggestions, key=lambda x: -x['confidence'])


def find_natural_positions(words, sentence_text, keyword, sentence_start):
    """
    Given word/POS info for a sentence, suggest natural insertion locations.

    Returns:
        list of dicts: Each dict has 'position', 'context', 'confidence', 'insertion_type'.
    """
    positions = []
    for i, word in enumerate(words):
        pos = word.get("partOfSpeech", "")
        lemma = word.get("lemma", "")
        word_start = word.get("startingPos", 0) - sentence_start

        # Rule 1: After adjectives, before nouns (for noun keywords)
        if pos.startswith("JJ") and i < len(words) - 1:
            next_word = words[i + 1]
            if next_word.get("partOfSpeech", "").startswith("NN"):
                confidence = 0.8
                positions.append({
                    'position': sentence_start + word_start + len(word.get("token", "")),
                    'context': f"after '{lemma}' before '{next_word.get('lemma', '')}'",
                    'confidence': confidence,
                    'insertion_type': 'adjective_noun'
                })

        # Rule 2: After prepositions (for noun keywords)
        if pos in ["IN", "TO"] and keyword_is_noun(keyword):
            confidence = 0.7
            positions.append({
                'position': sentence_start + word_start + len(word.get("token", "")),
                'context': f"after preposition '{lemma}'",
                'confidence': confidence,
                'insertion_type': 'after_preposition'
            })

        # Rule 3: Before conjunctions (and/or)
        if pos in ["CC"] and lemma.lower() in ["and", "or"]:
            confidence = 0.6
            positions.append({
                'position': sentence_start + word_start,
                'context': f"before conjunction '{lemma}'",
                'confidence': confidence,
                'insertion_type': 'before_conjunction'
            })
    return positions


def keyword_is_noun(keyword):
    """
    Simple heuristic to check if keyword is likely a noun.
    Could be enhanced with an actual POS tagger if needed.
    """
    return not keyword.lower() in [
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'
    ]
