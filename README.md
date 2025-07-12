# SEO Audit Web Application

A comprehensive, enterprise-grade SEO audit tool that analyzes website SEO performance and generates detailed reports with visual presentations. Features both web interface and sophisticated CLI tools for professional SEO analysis.

## 🚀 Key Features

### 🔍 **Advanced Web Crawling & Analysis**
- **Intelligent Crawling**: Crawls websites with configurable depth and page limits
- **Multi-Language Support**: Korean and English content analysis with appropriate tokenization
- **Knowledge Graph Generation**: Builds comprehensive keyword relationship maps using NetworkX
- **Content Extraction**: Advanced text analysis with readability scoring and keyword density
- **Link Analysis**: Internal/external link classification and relationship mapping

### 🔧 **Technical SEO Audit**
- **Infrastructure Analysis**: robots.txt, sitemap.xml, and site structure evaluation
- **Core Web Vitals**: LCP, FID, and CLS performance metrics
- **Security Assessment**: HTTPS, canonical links, and security headers
- **Mobile Optimization**: Mobile-friendliness and responsive design checks
- **Structured Data**: Schema.org markup validation and recommendations

### 📊 **On-Page SEO Analysis**
- **Page Ranking**: Identifies top 20 most important pages using proprietary scoring
- **Content Optimization**: Title, meta description, and heading tag analysis
- **URL Structure**: SEO-friendly URL pattern evaluation
- **Social Media Integration**: Open Graph and Twitter Card validation
- **Image Optimization**: Alt text and image SEO best practices

### 📈 **Comprehensive Reporting**
- **Multi-Format Output**: JSON, Markdown, HTML reports with detailed insights
- **Weighted Scoring**: Advanced scoring algorithm considering multiple SEO factors
- **Actionable Recommendations**: Priority-based improvement suggestions
- **Issue Tracking**: Critical, warning, and informational issue classification
- **Progress Monitoring**: Historical data comparison and trend analysis

### 🎨 **Professional Visualizations**
- **Dynamic Charts**: matplotlib-powered charts with Korean font support
- **Interactive Presentations**: HTML presentations with slide navigation
- **Export Options**: PPTX and PDF formats for client presentations
- **Custom Styling**: Clean, minimal design with effective data visualization
- **Responsive Design**: Mobile-friendly report viewing

### 🖥️ **CLI Interface** (New!)
- **Command-line Tools**: Professional CLI for automated workflows
- **Interactive Mode**: Guided audit setup with intelligent prompts
- **Batch Processing**: Multiple website analysis with queue management
- **Data Persistence**: Cached results and incremental updates
- **Server Management**: Graceful start/stop with process monitoring

### 🛠️ **Enterprise Features**
- **Data Caching**: Intelligent caching to avoid redundant crawls
- **Session Management**: Secure session handling with UUID-based tracking
- **Error Recovery**: Robust error handling with graceful degradation
- **Logging**: Comprehensive logging for debugging and monitoring
- **Scalability**: Modular architecture supporting high-volume analysis

## 📋 Prerequisites

### System Requirements
- **Python 3.8+**: Required for all functionality
- **pip**: Python package manager
- **Virtual Environment**: Strongly recommended for isolation

### macOS-Specific Requirements
For full PDF generation support, install system libraries:
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install WeasyPrint dependencies
brew install pango gdk-pixbuf libffi gobject-introspection gtk+3 cairo glib
```

### NLTK Data Setup
The application uses custom NLTK data location:
```bash
# Move NLTK data to ~/Utilities/nltk_data for optimal performance
mkdir -p ~/Utilities/nltk_data
# Or the application will auto-download to this location
```

## 🛠️ Installation

### Quick Setup
```bash
# Clone repository
git clone <repository-url>
cd seo-audit-basic

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py
```

### Development Setup
```bash
# After basic setup, verify installation
python -c "from src.main import app; print('✅ Installation successful')"

# Test core functionality
python simple_test.py
```

## 🚀 Usage

### Web Interface

#### Development Mode
```bash
# Start the Flask development server
python src/main.py

# Access the web interface
# http://localhost:5001
```

#### Production Deployment
```bash
# Using Gunicorn (Linux/Mac)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 'src.main:app'

# Using Waitress (Windows)
pip install waitress
waitress-serve --port=5001 src.main:app
```

### CLI Interface (Advanced)

#### Basic Commands
```bash
# Start interactive SEO audit
python cli.py audit --interactive

# Quick audit with URL
python cli.py audit --url https://example.com

# Start web server with options
python cli.py server --port 5001 --host 0.0.0.0

# Check cached data
python cli.py cache --list

# View audit history
python cli.py history --website example.com
```

#### Interactive Mode
```bash
# Launch interactive CLI
python cli.py --interactive

# Follow guided prompts for:
# - Website URL input with validation
# - Crawl depth and page limit configuration
# - Output format selection
# - Report delivery options
```

#### Batch Processing
```bash
# Process multiple websites
python cli.py batch --file websites.txt

# Schedule recurring audits
python cli.py schedule --url https://example.com --interval weekly
```

### User Guide

#### Web Interface Workflow
1. **Navigate to** `http://localhost:5001`
2. **Enter website URL** in the audit form
3. **Click "분석 시작"** to begin analysis
4. **Monitor progress** on the status page
5. **View results** in interactive presentation
6. **Download reports** in PPTX/PDF format

#### CLI Workflow
1. **Start interactive mode**: `python cli.py --interactive`
2. **Enter website URL** when prompted
3. **Configure options** (depth, pages, format)
4. **Monitor progress** with real-time updates
5. **Access results** via generated file paths
6. **Manage cache** for repeated audits

#### Report Interpretation
- **Overall Score**: Weighted average of all SEO factors
- **Technical SEO**: Infrastructure and crawlability issues
- **On-Page SEO**: Content optimization opportunities
- **Priority Issues**: Critical problems requiring immediate attention
- **Recommendations**: Actionable steps for improvement

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

## 🔧 Troubleshooting

### Common Issues

#### **Installation Problems**
```bash
# WeasyPrint dependency issues (macOS)
brew install pango gdk-pixbuf libffi gobject-introspection gtk+3 cairo glib

# NLTK data issues
mkdir -p ~/Utilities/nltk_data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Virtual environment issues
deactivate && rm -rf venv && python -m venv venv && source venv/bin/activate
```

#### **Runtime Errors**
```bash
# 500 Internal Server Error
tail -f seo_audit.log  # Check logs
chmod 666 src/seo_audit.db  # Fix database permissions
mkdir -p src/static/{uploads,reports,charts,presentations}  # Create directories

# Import errors (Link model, etc.)
python -c "from src.analyzer.technical_seo_checker import TechnicalSEOChecker; print('✅ Imports OK')"

# Font issues (Korean text)
python -c "import matplotlib.pyplot as plt; print('✅ Matplotlib OK')"
```

#### **Database Issues**
```bash
# Reinitialize database
rm -f src/seo_audit.db instance/seo_audit.db
python init_db.py

# Check database integrity
sqlite3 instance/seo_audit.db ".tables"
```

#### **Performance Issues**
```bash
# Clear cache
python cli.py cache --clear

# Reduce crawl limits
# Edit main.py: crawler = SEOCrawler(url, max_pages=10, max_depth=2)

# Check system resources
top -pid $(pgrep -f "python.*main.py")
```

### Recent Fixes Applied

✅ **Fixed WeasyPrint Import Issues** - Added graceful fallback for PDF generation  
✅ **Fixed Font Configuration** - Dynamic Korean font detection on macOS  
✅ **Fixed Link Model Import** - Added missing imports in technical_seo_checker.py  
✅ **Fixed NLTK Data Path** - Custom path configuration for ~/Utilities/nltk_data  
✅ **Fixed URL Normalization** - Proper handling of trailing slashes  
✅ **Fixed Error Handling** - Comprehensive error handling with detailed logging  
✅ **Fixed Chart Generation** - Robust chart creation with fallback options  
✅ **Fixed Presentation Design** - Error recovery for missing dependencies  

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