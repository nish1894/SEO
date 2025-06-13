# analyzer/forms.py
"""
URLForm

Defines a Django form for accepting and validating a website URL.

Fields:
- url (URLField): Ensures a syntactically valid URL.

Validation:
- Performs an HTTP HEAD request with a 10-second timeout to verify the URL is reachable.
  Raises a ValidationError if the site is down or unreachable.
"""
from django import forms
import requests


class URLForm(forms.Form):
    url = forms.URLField(
        label="Site URL",
        widget=forms.URLInput(
            attrs={
                "placeholder": "https://example.com",
                "class": "w-full rounded-full border border-gray-300 px-4 py-2 focus:outline-none "
                         "focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
            }
        ),
    )

    def clean_url(self):
        """
        Verify that the provided URL is reachable by issuing a HEAD request.

        Returns:
            str: The cleaned URL if reachable.

        Raises:
            forms.ValidationError: If the URL cannot be reached or returns a bad status.
        """
        value = self.cleaned_data['url']
        try:
            response = requests.head(value, timeout=10, allow_redirects=True)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            raise forms.ValidationError(
                "Cannot reach that URL. Please make sure it starts with http:// or https:// "
                "and that the site is up."
            )
        return value
