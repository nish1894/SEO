def insert_keyword_smart(text, keyword):
    # Insert the keyword near the start if it's not already in the text.
    if keyword.lower() in text.lower():
        return text  # Don't duplicate
    sentences = text.split('.')
    # Insert keyword in the middle of the first sentence
    if sentences:
        sentences[0] += f" {keyword}"
    new_text = '.'.join(sentences)
    return new_text
