# --- Utility for Smart Keyword Insertion into Text ---

def insert_keyword_smart(data_json, text, keyword):
    """
    Main entrypoint: Given Textrazor-parsed data, text, and a keyword,
    suggest and perform a natural insertion.
    """
    if keyword.lower() in text.lower():
        return text  # Don't duplicate

    insertion_suggestions = find_insertion_points(data_json, text, [keyword])

    # If we have good suggestions, pick the best one
    if insertion_suggestions:
        # Generate candidate texts for user to pick, or just pick the best one
        options = generate_insertion_options(text, insertion_suggestions)
        # Pick the top option (highest confidence)
        return options[0]["new_text"]

    # Fallback: insert keyword at the end of the first sentence
    sentences = text.split('.')
    if sentences:
        sentences[0] = sentences[0].strip() + f" {keyword}"
    return '.'.join(sentences)


def generate_insertion_options(original_text, insertion_suggestions):
    """
    Generate multiple insertion options for user to choose from.
    Each suggestion gets templates for context.
    """
    options = []
    for suggestion in insertion_suggestions[:5]:  # Top 5
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
    """Create natural insertion templates based on context"""
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
    """Get a preview of the text around the insertion point"""
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
    """Find natural insertion points for keywords in the text (using Textrazor output)"""
    sentences = data_json.get("sentences", [])
    insertion_suggestions = []
    for keyword in keywords:
        keyword_lower = keyword.lower()
        for sentence in sentences:
            sentence_text = sentence.get("text", "")
            sentence_start = sentence.get("startingPos", 0)
            # Skip if keyword already exists in sentence
            if keyword_lower in sentence_text.lower():
                continue
            words = sentence.get("words", [])
            # Find natural insertion points
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
    # Sort by confidence
    return sorted(insertion_suggestions, key=lambda x: -x['confidence'])


def find_natural_positions(words, sentence_text, keyword, sentence_start):
    """Find natural positions within a sentence to insert keywords"""
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
        # Rule 3: Before conjunctions for additional context
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
    """Simple heuristic to check if keyword is likely a noun"""
    # (You could enhance this with a POS tagger if needed)
    return not keyword.lower() in ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']

