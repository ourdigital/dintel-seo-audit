# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an SEO audit web application built with Flask that crawls websites, analyzes SEO metrics, and generates comprehensive reports and presentations. The application supports both Korean and English content analysis and follows a modular architecture with clear separation of concerns.

## Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python init_db.py
```

## Development Commands

```bash
# Run the application in development mode
python src/main.py

# Access the application at
# http://localhost:5000

# Test basic functionality
python simple_test.py

# Initialize database manually
python init_db.py
```

## Production Deployment

```bash
# For Linux/Mac
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'src.main:app'

# For Windows
pip install waitress
waitress-serve --port=5000 src.main:app
```

## Core Architecture

The application follows a modular architecture with several key components:

1. **Crawler Module**: Handles website crawling, text extraction, and initial data collection.
   - `SEOCrawler`: Crawls websites, extracts content, links, and metadata.
   - `SEODataImporter`: Imports crawled data into the database.

2. **Analyzer Module**: Performs various analyses on the collected data.
   - `TextAnalyzer`: Analyzes text content and keywords.
   - `TechnicalSEOChecker`: Checks technical SEO aspects like robots.txt, sitemap.xml, etc.
   - `PageRanker`: Ranks pages based on SEO metrics.
   - `OnPageSEOAnalyzer`: Analyzes on-page SEO elements.

3. **Report Module**: Generates comprehensive reports based on analysis results.
   - `ReportGenerator`: Creates text reports and JSON data for visualization.

4. **Presentation Module**: Creates visual presentations of the SEO audit results.
   - `PresentationDesigner`: Designs visual elements, charts, and generates PPTX/PDF presentations.

5. **Data Models**: SQLAlchemy models for storing data.
   - `Website`: Represents a website being analyzed.
   - `Page`: Represents individual pages of a website.
   - `Keyword`: Stores keyword information for each page.
   - `Link`: Stores link information for each page.
   - `TechnicalSEO`: Stores technical SEO data for a website.

6. **Main Application**: Flask application handling routes and orchestrating the SEO audit process.

## Workflow

1. User submits a URL for analysis.
2. Application crawls the website (limited to 50 pages by default).
3. Extracted data is stored in the database.
4. Various analyzers process the data and generate insights.
5. Results are compiled into comprehensive reports.
6. Visual presentations (HTML, PPTX, PDF) are generated for the user.
7. User can view the results and download the reports.

## Troubleshooting

If you encounter a 500 error:

1. Check logs:
```bash
tail -f seo_audit.log
```

2. Ensure database has proper permissions:
```bash
chmod 666 src/seo_audit.db
```

3. Verify all required directories exist:
```bash
mkdir -p src/static/{uploads,reports,charts,presentations}
```

4. Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```