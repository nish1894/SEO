# analyzer/forms.py
from django import forms
import requests

class URLForm(forms.Form):
    url = forms.URLField(
        label="Site URL",
        widget=forms.URLInput(attrs={"placeholder": "https://example.com", "class": "w-full"}),
    )

    def clean_url(self):
        value = self.cleaned_data['url']
        # Quick head request to see if the site exists
        try:
            resp = requests.head(value, timeout=20, allow_redirects=True)
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            raise forms.ValidationError(
                "Cannot reach that URL. Please make sure it starts with http:// or https:// "
                "and that the site is up."
            )
        return value
