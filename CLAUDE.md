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

The application follows a modular architecture with clear separation of concerns:

### 1. **Crawler Module** (`src/crawler/`)
- **`SEOCrawler`**: Main crawler that extracts content, metadata, links, and builds knowledge graphs using NetworkX. Supports configurable depth and page limits.
- **`SEODataImporter`**: Handles data persistence, imports crawled JSON data into SQLite database with transaction management.

### 2. **Analyzer Module** (`src/analyzer/`)
- **`TextAnalyzer`**: Performs multilingual content analysis including keyword extraction, density calculation, and readability scoring for Korean and English.
- **`TechnicalSEOChecker`**: Comprehensive technical SEO audit covering robots.txt, sitemap.xml, Core Web Vitals, meta tags, and mobile-friendliness.
- **`PageRanker`**: Calculates page importance scores based on homepage status, depth, internal links, and content quality.
- **`OnPageSEOAnalyzer`**: Detailed page-level analysis including title optimization, URL structure, heading evaluation, and social media tags.

### 3. **Report Module** (`src/report/`)
- **`ReportGenerator`**: Creates comprehensive reports in JSON, Markdown, and HTML formats with weighted SEO scores and actionable recommendations.

### 4. **Presentation Module** (`src/presentation/`)
- **`PresentationDesigner`**: Generates charts using matplotlib and creates interactive HTML presentations with PPTX/PDF export capabilities.

### 5. **Data Models** (`src/models/`)
SQLAlchemy models with proper relationships:
- `Website`: Main website entity with pages and technical SEO data
- `Page`: Individual page data with keywords and links
- `Keyword`: Keyword frequency and density data
- `Link`: Internal/external link relationships
- `TechnicalSEO`: Technical SEO audit results

### 6. **Flask Application** (`src/main.py`)
Session-based API with endpoints for audit processing, status checking, and result delivery.

## Key Features

- **Multi-language support**: Korean and English text analysis with appropriate tokenization
- **Comprehensive SEO analysis**: Technical, on-page, and keyword analysis
- **Visual reporting**: Multiple chart types with professional styling
- **Export capabilities**: HTML, PPTX, and PDF formats
- **Scalable architecture**: Modular design with database-driven persistence

## Workflow

1. User submits URL → Session ID generation
2. Website crawling (max 50 pages, depth 3) → Data extraction
3. Database import → Multi-phase analysis (text, technical, ranking, on-page)
4. Report generation → Visual presentation creation
5. Results available via web interface and downloadable formats

## Recent Development Progress

### Major Bugs Fixed ✅
1. **WeasyPrint Import Issues** - Added graceful fallback for PDF generation when system libraries are missing
2. **Font Configuration** - Dynamic Korean font detection on macOS (now uses AppleGothic)
3. **Link Model Import** - Fixed missing imports in technical_seo_checker.py causing NameError
4. **NLTK Data Path** - Custom path configuration for ~/Utilities/nltk_data to avoid conflicts
5. **URL Normalization** - Proper handling of trailing slashes in website queries
6. **Error Handling** - Comprehensive error handling with detailed logging and graceful degradation
7. **Chart Generation** - Robust chart creation with fallback options for missing data
8. **Presentation Design** - Error recovery for missing dependencies with mock classes

### New Features Added 🚀
1. **Enhanced Error Logging** - Detailed stack traces and error context in main.py
2. **Font Auto-Detection** - Dynamic font selection based on available system fonts
3. **Mock PresentationDesigner** - Graceful fallback when dependencies are missing
4. **Improved Import Handling** - Conditional imports with fallback classes
5. **Better Chart Error Handling** - Individual chart generation with try/catch blocks
6. **Enhanced Database Queries** - Better URL normalization and website lookup

### Development Notes

#### Database Management
- SQLite database with automatic table creation at `instance/seo_audit.db`
- Session-based data isolation using secure_filename for directory names
- Database initialization handled by `init_db.py` with proper error handling
- URL normalization for consistent website lookups

#### File Structure
- **Static files**: `src/static/` contains uploads, reports, charts, and presentations
- **Templates**: `src/templates/` contains HTML templates for web interface
- **Session data**: Each audit creates a session directory with JSON results
- **NLTK data**: Custom location at `~/Utilities/nltk_data` for consistent access

#### Key Dependencies
- **Flask + SQLAlchemy**: Web framework and ORM
- **BeautifulSoup4 + NLTK**: HTML parsing and text analysis
- **NetworkX**: Graph analysis for knowledge graphs
- **matplotlib**: Chart generation with Korean font support
- **python-pptx + WeasyPrint**: Document generation (with fallback support)

#### Configuration
- Crawl limits: 50 pages max, depth 3 (configurable in main.py:89)
- Database: SQLite with automatic table creation
- File uploads: Secure filename handling with session isolation
- Font detection: Automatic Korean font selection on macOS
- Error handling: Comprehensive logging and graceful degradation

#### System Requirements
- **macOS**: Requires Homebrew packages for WeasyPrint (pango, gdk-pixbuf, etc.)
- **NLTK**: Custom data path at ~/Utilities/nltk_data
- **Python 3.8+**: Required for all functionality
- **Virtual environment**: Strongly recommended for dependency isolation

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