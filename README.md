# SEO Audit Web Application

A comprehensive SEO audit tool for small websites that analyzes website SEO performance and generates detailed reports with visual presentations.

## Features

### 🔍 **Web Crawling & Text Analysis**
- Crawls websites and extracts text data, metadata, and links
- Performs keyword density analysis and builds knowledge graphs
- Supports both Korean and English content analysis
- Configurable crawl limits (50 pages max, depth 3)

### 🔧 **Technical SEO Audit**
- Analyzes robots.txt and sitemap.xml
- Checks site structure and Core Web Vitals
- Evaluates redirects, canonical links, and meta tags
- Assesses mobile-friendliness and security

### 📊 **On-Page SEO Analysis**
- Identifies top 20 most important pages
- Analyzes SEO elements for each page
- Evaluates title optimization, URL structure, and content quality
- Checks heading tags and social media integration

### 📈 **Comprehensive Reporting**
- Generates detailed reports in multiple formats (JSON, Markdown, HTML)
- Provides current status, potential issues, and improvement recommendations
- Includes weighted SEO scores and actionable priority lists

### 🎨 **Visual Presentations**
- Creates professional charts and graphs using matplotlib
- Generates interactive HTML presentations
- Exports to PPTX and PDF formats
- Clean, minimal design with effective data visualization

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Steps

1. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Initialize database:**
```bash
python init_db.py
```

## Usage

### Development Mode

1. **Start the application:**
```bash
python src/main.py
```

2. **Access the web interface:**
```
http://localhost:5000
```

3. **Test basic functionality:**
```bash
python simple_test.py
```

### Production Deployment

For production environments, use a WSGI server:

#### Using Gunicorn (Linux/Mac)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'src.main:app'
```

#### Using Waitress (Windows)
```bash
pip install waitress
waitress-serve --port=5000 src.main:app
```

## Project Structure

```
seo-audit-basic/
├── src/                    # Source code
│   ├── analyzer/           # Analysis modules
│   │   ├── text_analyzer.py
│   │   ├── technical_seo_checker.py
│   │   ├── page_ranker.py
│   │   └── onpage_seo_analyzer.py
│   ├── crawler/            # Crawling modules
│   │   ├── seo_crawler.py
│   │   └── data_importer.py
│   ├── models/             # Data models
│   │   └── seo_data.py
│   ├── presentation/       # Presentation module
│   │   └── presentation_designer.py
│   ├── report/             # Report generation
│   │   └── report_generator.py
│   ├── static/             # Static files
│   │   ├── charts/         # Generated charts
│   │   ├── presentations/  # Presentation files
│   │   ├── reports/        # Report files
│   │   └── uploads/        # Upload files
│   ├── templates/          # HTML templates
│   └── main.py             # Main Flask application
├── init_db.py              # Database initialization script
├── requirements.txt        # Python dependencies
├── CLAUDE.md              # Claude Code guidance
└── README.md              # This file
```

## Architecture

The application follows a modular architecture with clear separation of concerns:

- **Crawler Module**: Handles website crawling and data extraction
- **Analyzer Module**: Performs various SEO analyses (text, technical, on-page)
- **Report Module**: Generates comprehensive reports
- **Presentation Module**: Creates visual presentations and exports
- **Data Models**: SQLAlchemy models for data persistence

## Technology Stack

- **Backend**: Flask, SQLAlchemy, SQLite
- **Analysis**: BeautifulSoup4, NLTK, NetworkX
- **Visualization**: matplotlib, plotly
- **Export**: python-pptx, WeasyPrint
- **Frontend**: HTML, CSS, JavaScript

## API Endpoints

- `POST /audit` - Start SEO audit
- `GET /audit/<session_id>/status` - Check audit status
- `GET /presentation/<session_id>` - View HTML presentation
- `GET /download/<session_id>/pptx` - Download PPTX report
- `GET /download/<session_id>/pdf` - Download PDF report

## Troubleshooting

### Common Issues

**500 Internal Server Error:**
1. Check application logs:
```bash
tail -f seo_audit.log
```

2. Verify database permissions:
```bash
chmod 666 src/seo_audit.db
```

3. Ensure required directories exist:
```bash
mkdir -p src/static/{uploads,reports,charts,presentations}
```

4. Reinstall dependencies:
```bash
pip install -r requirements.txt
```

**Database Issues:**
- Run database initialization: `python init_db.py`
- Check SQLite file permissions
- Verify database schema creation

**Missing Dependencies:**
- Ensure all packages from requirements.txt are installed
- Check for version conflicts
- Use virtual environment to isolate dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the CLAUDE.md file for development guidance
- Create an issue in the project repository