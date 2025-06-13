# analyzer/utils/seo_optimizer.py

from textblob import TextBlob


class SeoOptimizer:
    def __init__(self, text, main_keywords, semantic_keywords, readability, stats):
        self.text = text
        self.main_keywords = main_keywords or []
        self.semantic_keywords = semantic_keywords or []
        self.readability = readability or {}
        self.stats = stats or {}
        self.opportunities = []

    def analyze(self):
        self.check_semantic_keywords()
        self.check_long_sentences()
        self.check_large_paragraphs()
        self.check_passive_voice()
        self.check_reading_grade()
        return self.opportunities


    def check_semantic_keywords(self):
        missing = [k for k in self.semantic_keywords if k.lower() not in self.text.lower()]
        if missing:
            self.opportunities.append(
                f"Consider including related terms: {', '.join(missing)}."
            )

    def check_long_sentences(self, max_len=25):
        blob = TextBlob(self.text)
        long_sents = [str(s) for s in blob.sentences if len(str(s).split()) > max_len]
        if long_sents:
            self.opportunities.append(f"{len(long_sents)} sentence(s) are too long. Try splitting them.")

    def check_large_paragraphs(self, max_words=80):
        paragraphs = self.text.split('\n\n')
        large = [p for p in paragraphs if len(p.split()) > max_words]
        if large:
            self.opportunities.append("Break up paragraphs with more than 80 words for easier reading.")


    def check_passive_voice(self):
        blob = TextBlob(self.text)
        passive = [str(s) for s in blob.sentences if " by " in str(s)]
        if len(passive) > 0 and len(passive) > len(blob.sentences) * 0.3:
            self.opportunities.append("Reduce passive voice. Rewrite sentences to be more direct.")

    def check_reading_grade(self, max_grade=10):
        grade = self.readability.get("flesch_kincaid_grade", 0)
        if grade > max_grade:
            self.opportunities.append("Lower the reading grade for a broader audience.")





# Usage Example (in your main analysis logic):

# from analyzer.utils.seo_optimizer import SEOOptimizer

# optimizer = SEOOptimizer(
#     text=your_text,
#     main_keywords=["your", "main", "keywords"],
#     semantic_keywords=["semantic", "related", "terms"],
#     readability=your_readability_dict,
#     stats=your_stats_dict
# )
# opportunities = optimizer.analyze()
