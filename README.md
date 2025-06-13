# Django SEO Analyzer

A Django-based web application to analyze website SEO and performance metrics using Google PageSpeed Insights API and display results with an interactive, HTMX-powered interface.

## Features

* **URL Validation**: Ensures entered URLs are syntactically valid and reachable via an HTTP HEAD request.
* **PageSpeed Insights Integration**: Fetches SEO-related audits (document-title, meta-description, link-text, etc.) from Google PSI.
* **Visual Report**: Displays overall score with a gauge, summary boxes, and detailed audit results.
* **History**: Keeps the last three analyses in session and allows quick retrieval without re-querying the API.
* **HTMX**: Partial page updates, loading overlay, and fast, responsive interactions without full page reloads.
* **Tailwind CSS**: Modern, responsive styling with utility-first classes.

## Getting Started

### Prerequisites

* Python 3.9+
* Django 5.2+
* `requests`, `beautifulsoup4`, `django-htmx`

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/seo-analyzer.git
   cd seo-analyzer
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate    # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file or export:

   ```bash
   export GOOGLE_PSI_API_KEY=your_api_key_here
   export PSI_ENDPOINT=https://www.googleapis.com/pagespeedonline/v5/runPagespeed
   ```

5. **Run migrations and start the server**

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

6. **Visit** `http://127.0.0.1:8000/` in your browser.

## Usage

1. Paste a URL into the input field and click **Submit**.
2. View the colored gauge and detailed audit results.
3. Recent searches display below; click to revisit.

## Project Structure

```
seo-analyzer/
├── analyzer/
│   ├── forms.py          # URLForm with validation
│   ├── utils/
│   │   ├── pagespeed.py  # API integration & scoring logic
│   │   └── fevicon.py    # Favicon scraping utility
│   ├── views.py          # Django views with HTMX support
│   ├── urls.py           # URL routing for analyzer app
│   └── templates/analyzer
│       ├── home.html
│       ├── psi_fragment.html
│       └── recent_searches.html
├── templates/base.html    # Base layout with HTMX & loading overlay
├── static/                # Static assets (Tailwind, HTMX)
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## License

MIT License © Your Name
