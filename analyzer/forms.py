# analyzer/forms.py

from django import forms

class TextForm(forms.Form):
    """
    Django form for accepting a block of user text (blog post, tweet thread, etc.)
    Validates that the content is not empty and meets a minimum length.
    """
    content = forms.CharField(
        label="Your Text",
        widget=forms.Textarea(attrs={
            "placeholder": "Paste your blog, tweet, or caption here…",
            "rows": 6,
            "class": (
                "w-full rounded-lg border border-gray-300 px-4 py-2 "
                "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            ),
        }),
        help_text="Enter at least 20 characters.",
        min_length=10,
        required=True,
        error_messages={
            'required': "Please enter some text!",
            'min_length': "Your text is too short (minimum 10 characters)."
        }
    )
