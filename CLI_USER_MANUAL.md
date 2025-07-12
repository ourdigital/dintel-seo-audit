# SEO Audit CLI - User Manual

## 📖 Overview

The SEO Audit CLI is a comprehensive command-line tool for analyzing website SEO performance. It provides both interactive and automated workflows for professional SEO auditing.

## 🚀 Quick Start

```bash
# Get help
python cli.py --help

# Interactive mode (recommended for beginners)
python cli.py --interactive

# Quick audit
python cli.py audit --url https://example.com
```

## 📋 Available Commands

### 1. **Interactive Mode** 
*Guided audit setup with step-by-step prompts*

```bash
python cli.py --interactive
# OR
python cli.py -i
```

**What it does:**
- Guides you through website URL input with validation
- Configures crawl settings (pages, depth) interactively
- Checks for cached results and offers to reuse them
- Lets you choose output formats (HTML, PPTX, PDF)
- Runs complete 8-step audit process
- Displays results with file locations

**Best for:** First-time users, client demonstrations, when you need guidance

---

### 2. **Audit Command**
*Direct SEO audit execution*

```bash
# Basic audit
python cli.py audit --url https://example.com

# Customized audit
python cli.py audit --url https://example.com --max-pages 25 --max-depth 4

# Interactive audit mode
python cli.py audit --url https://example.com --interactive
```

**Options:**
- `--url, -u`: Website URL to audit (required)
- `--max-pages, -p`: Maximum pages to crawl (default: 50)
- `--max-depth, -d`: Maximum crawl depth (default: 3)
- `--interactive`: Use interactive mode for this audit

**What it does:**
- Crawls specified website up to max pages/depth
- Performs complete SEO analysis (technical + on-page)
- Generates reports in all formats (HTML, PPTX, PDF)
- Stores results in cache for future reference
- Displays audit scores and file locations

**Best for:** Automated workflows, scripting, quick audits

---

### 3. **Server Management**
*Control the web server interface*

```bash
# Start server (default: localhost:5001)
python cli.py server

# Start on custom host/port
python cli.py server --host 0.0.0.0 --port 8080

# Stop server
python cli.py server --stop
```

**Options:**
- `--host`: Server host address (default: localhost)
- `--port, -p`: Server port (default: 5001)
- `--stop`: Stop the running server

**What it does:**
- Starts Flask web server for browser-based audits
- Monitors server process and handles graceful shutdown
- Checks port availability before starting
- Provides web interface at specified host:port

**Best for:** Web interface access, team collaboration, client presentations

---

### 4. **Cache Management**
*Manage stored audit results*

```bash
# List all cached audits
python cli.py cache --list
# OR
python cli.py cache -l

# Clear all cached data
python cli.py cache --clear
# OR
python cli.py cache -c
```

**Options:**
- `--list, -l`: Display all cached audit results with timestamps
- `--clear, -c`: Remove all cached audit data

**What it does:**
- Shows cached audits with creation dates and status
- Manages SQLite cache database in ~/.seo_audit/
- Helps avoid redundant audits of same websites
- Provides cleanup functionality for storage management

**Best for:** Managing storage, avoiding duplicate work, cleanup

---

### 5. **History Command**
*View audit history and trends*

```bash
# View all audit history
python cli.py history

# Filter by specific website
python cli.py history --website example.com
```

**Options:**
- `--website, -w`: Filter results by website domain

**What it does:**
- Displays chronological audit history
- Shows audit status and completion dates
- Allows filtering by website
- Currently uses same data as cache command

**Best for:** Tracking audit history, client progress monitoring

---

## 🎯 Common Usage Patterns

### For SEO Professionals

```bash
# Client audit workflow
python cli.py --interactive                    # Guided setup
python cli.py audit --url client-site.com     # Quick follow-up
python cli.py cache --list                    # Review past audits
```

### For Developers

```bash
# Automated testing
python cli.py audit --url staging.site.com --max-pages 10
python cli.py audit --url production.site.com --max-pages 50
python cli.py cache --clear                   # Cleanup after testing
```

### For Agencies

```bash
# Client demonstration
python cli.py server --port 8080              # Start web interface
python cli.py --interactive                   # Guided audit demo
python cli.py history --website client.com    # Show progress
```

### For Content Teams

```bash
# Regular monitoring
python cli.py audit --url blog.company.com --max-pages 25
python cli.py cache --list                    # Check recent audits
```

## 📊 Understanding Output

### Audit Results Display
```
Website: https://example.com
Overall Score: 75.2/100
Technical SEO: 68.5/100
On-Page SEO: 81.8/100

Generated Files:
  HTML: /path/to/presentation.html
  PPTX: /path/to/presentation.pptx
  PDF: /path/to/presentation.pdf
```

### Cache List Display
```
✅ https://example.com (Created: 2025-07-12 14:30:15)
🔄 https://test-site.com (Created: 2025-07-12 14:25:08)
❌ https://failed-site.com (Created: 2025-07-12 14:20:33)
```

**Status Icons:**
- ✅ Completed successfully
- 🔄 Currently running
- ❌ Failed/incomplete

## ⚙️ Configuration & Settings

### Cache Location
Audit results are stored in: `~/.seo_audit/cache.db`

### Output Files
Generated reports are saved in: `~/.seo_audit/reports/[site-hash]/`

### Logs
- General logs: `seo_audit.log`
- Error logs: `seo_audit_errors.log`

## 🔧 Advanced Options

### Environment Variables
```bash
export FLASK_HOST=0.0.0.0      # Default server host
export FLASK_PORT=5001         # Default server port
```

### Crawl Limits
- **Max Pages**: 1-1000 (recommended: 10-50 for most sites)
- **Max Depth**: 1-10 (recommended: 2-4 for most sites)
- **Timeout**: 30 minutes per audit

### Performance Tuning
```bash
# For large sites
python cli.py audit --url large-site.com --max-pages 100 --max-depth 2

# For quick checks
python cli.py audit --url quick-check.com --max-pages 5 --max-depth 1
```

## 🚨 Error Handling

### Common Issues & Solutions

**"URL is not specified"**
```bash
# Wrong: Missing --url
python cli.py audit example.com

# Correct: Include --url flag
python cli.py audit --url https://example.com
```

**"Port already in use"**
```bash
# Check what's using the port
lsof -i :5001

# Use different port
python cli.py server --port 5002
```

**"No cached audits found"**
```bash
# Run an audit first
python cli.py audit --url https://example.com

# Then check cache
python cli.py cache --list
```

### Timeout Issues
```bash
# For slow sites, monitor with performance tool
python performance_monitor.py --url slow-site.com
```

## 📈 Performance Guidelines

### Recommended Limits by Site Type

| Site Type | Max Pages | Max Depth | Est. Time |
|-----------|-----------|-----------|-----------|
| Small Business | 10-20 | 2-3 | 3-8 min |
| Blog/Content | 20-50 | 3-4 | 8-20 min |
| E-commerce | 30-100 | 2-3 | 15-40 min |
| Enterprise | 50-200 | 2-4 | 30-60 min |

### Resource Usage
- **Memory**: 200MB-1GB depending on site size
- **Storage**: 5-20MB per audit cache
- **Network**: 10-100MB depending on page content

## 🎯 Best Practices

### Before Running Audits
1. Check if site allows crawling (`robots.txt`)
2. Start with small page limits for unknown sites
3. Verify URL format includes `https://` or `http://`

### During Audits
1. Monitor progress through colored status messages
2. Use Ctrl+C to gracefully stop if needed
3. Check logs if unexpected behavior occurs

### After Audits
1. Review generated reports for actionable insights
2. Keep cache clean to manage storage
3. Document findings for client reports

## 🆘 Getting Help

### Built-in Help
```bash
python cli.py --help                 # Main help
python cli.py audit --help           # Audit command help
python cli.py server --help          # Server command help
python cli.py cache --help           # Cache command help
```

### Troubleshooting
```bash
# Check tool status
python cli.py cache --list

# Clear problematic cache
python cli.py cache --clear

# View detailed logs
tail -f seo_audit.log
```

### Example Workflows
See `field_test_suite.py` for comprehensive testing examples and usage patterns.

---

## 📞 Support

For issues or questions:
1. Check this manual for common solutions
2. Review log files for error details  
3. Use field testing tools to validate setup
4. Check CLAUDE.md for development guidance