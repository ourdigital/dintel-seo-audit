# SEO Audit CLI - Command Reference

## 🎯 Command Overview

| Command | Purpose | Best For |
|---------|---------|----------|
| `--interactive` | Guided audit setup | Beginners, demos |
| `audit` | Direct SEO audit | Automation, scripting |
| `server` | Web interface | Teams, presentations |
| `cache` | Manage results | Storage, efficiency |
| `history` | View trends | Monitoring, reports |
| `help` | Quick reference | Fast lookup |
| `manual` | Full documentation | Learning, troubleshooting |

---

## 📋 Command Details

### Interactive Mode
```bash
python cli.py --interactive
python cli.py -i
```
**Actions:**
- ✅ URL validation with auto-correction
- ✅ Crawl configuration (pages, depth)
- ✅ Cache checking and reuse options
- ✅ Output format selection
- ✅ Real-time progress tracking
- ✅ Results display with file paths

---

### Audit Command
```bash
# Basic syntax
python cli.py audit --url <URL> [OPTIONS]

# Examples
python cli.py audit --url https://example.com
python cli.py audit -u https://site.com -p 25 -d 2
python cli.py audit --url https://site.com --interactive
```

**Options:**
- `--url, -u` : Website URL (required)
- `--max-pages, -p` : Max pages (1-1000, default: 50)
- `--max-depth, -d` : Max depth (1-10, default: 3)
- `--interactive` : Use guided mode

**Actions:**
- ✅ 8-step SEO audit process
- ✅ Multi-language content analysis
- ✅ Technical + On-page SEO scoring
- ✅ Professional report generation
- ✅ Automatic caching for efficiency

---

### Server Management
```bash
# Start server
python cli.py server [OPTIONS]

# Examples
python cli.py server                        # localhost:5001
python cli.py server --port 8080           # localhost:8080
python cli.py server --host 0.0.0.0 --port 8080  # Public access
python cli.py server --stop                # Stop server
```

**Options:**
- `--host` : Server host (default: localhost)
- `--port, -p` : Server port (default: 5001)
- `--stop` : Stop running server

**Actions:**
- ✅ Flask web server startup
- ✅ Port availability checking
- ✅ Process monitoring
- ✅ Graceful shutdown handling
- ✅ Browser-based interface access

---

### Cache Management
```bash
# List cached audits
python cli.py cache --list
python cli.py cache -l

# Clear all cache
python cli.py cache --clear
python cli.py cache -c
```

**Options:**
- `--list, -l` : Show cached audits
- `--clear, -c` : Remove all cache data

**Actions:**
- ✅ SQLite cache database management
- ✅ Audit history display with timestamps
- ✅ Status tracking (completed/running/failed)
- ✅ Storage cleanup and optimization
- ✅ Cache reuse for efficiency

---

### History Tracking
```bash
# View all history
python cli.py history

# Filter by website
python cli.py history --website example.com
```

**Options:**
- `--website, -w` : Filter by domain

**Actions:**
- ✅ Chronological audit display
- ✅ Website-specific filtering
- ✅ Progress tracking over time
- ✅ Trend analysis support

---

### Help System
```bash
# Quick reference
python cli.py help

# Full help
python cli.py --help

# Command-specific help
python cli.py [command] --help

# Comprehensive manual
python cli.py manual
```

**Actions:**
- ✅ Command overview and examples
- ✅ Usage patterns and best practices
- ✅ Troubleshooting guides
- ✅ Performance guidelines

---

## 🚀 Usage Patterns

### New Users
```bash
# Start here
python cli.py help
python cli.py --interactive
python cli.py manual  # For detailed learning
```

### SEO Professionals
```bash
# Client workflow
python cli.py audit --url client-site.com --max-pages 30
python cli.py cache --list
python cli.py history --website client-site.com
```

### Developers
```bash
# Automated testing
python cli.py audit --url staging.site.com --max-pages 10
python cli.py audit --url production.site.com
python cli.py cache --clear  # Cleanup
```

### Agencies
```bash
# Client presentations
python cli.py server --port 8080
python cli.py --interactive  # Demo mode
python cli.py audit --url client1.com && python cli.py audit --url client2.com
```

### Content Teams
```bash
# Regular monitoring
python cli.py audit --url blog.company.com --max-pages 25
python cli.py history  # Track improvements
```

---

## 📊 Output Formats

### All Commands Generate:
- **HTML Presentation**: Interactive slides with navigation
- **PPTX Presentation**: PowerPoint format for meetings
- **PDF Report**: Professional print-ready document
- **JSON Data**: Raw data for integration
- **Cache Entry**: For future reference

### File Locations:
- **Reports**: `~/.seo_audit/reports/[site-hash]/`
- **Cache**: `~/.seo_audit/cache.db`
- **Logs**: `seo_audit.log`, `seo_audit_errors.log`

---

## ⚙️ Performance Guidelines

### Recommended Limits:

| Site Type | Command Example | Time |
|-----------|----------------|------|
| **Small** | `audit --url site.com -p 10 -d 2` | 2-5 min |
| **Medium** | `audit --url site.com -p 30 -d 3` | 8-15 min |
| **Large** | `audit --url site.com -p 100 -d 2` | 20-40 min |

### Resource Usage:
- **Memory**: 200MB - 1GB
- **Storage**: 5-20MB per audit
- **Network**: 10-100MB per audit

---

## 🔧 Advanced Features

### Environment Variables:
```bash
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5001
```

### Batch Processing:
```bash
# Sequential audits
python cli.py audit --url site1.com && python cli.py audit --url site2.com

# With different settings
python cli.py audit --url blog.com -p 20 && python cli.py audit --url shop.com -p 50
```

### Performance Monitoring:
```bash
# Use performance monitor
python performance_monitor.py --url site.com --max-pages 50

# Use field test suite
python field_test_suite.py --url site.com
```

---

## 🚨 Common Issues & Solutions

### URL Format Errors
```bash
# ❌ Wrong
python cli.py audit --url example.com

# ✅ Correct
python cli.py audit --url https://example.com
```

### Port Conflicts
```bash
# ❌ Error: Port in use
python cli.py server

# ✅ Solution: Different port
python cli.py server --port 8080
```

### Cache Issues
```bash
# Clear problematic cache
python cli.py cache --clear

# Check cache status
python cli.py cache --list
```

### Performance Issues
```bash
# Reduce limits for slow sites
python cli.py audit --url slow-site.com -p 10 -d 1

# Monitor performance
python performance_monitor.py --url slow-site.com
```

---

## 📈 Audit Process Steps

Each `audit` command performs these 8 steps:

1. **Crawling**: Website discovery and content extraction
2. **Data Import**: Store pages, links, and metadata
3. **Text Analysis**: Keyword extraction and content analysis
4. **Technical SEO**: robots.txt, sitemap, Core Web Vitals
5. **Page Ranking**: Identify most important pages
6. **On-Page SEO**: Meta tags, headings, content optimization
7. **Report Generation**: Compile findings and scoring
8. **Presentation**: Create HTML, PPTX, and PDF outputs

### Progress Tracking:
- ✅ Green checkmarks for completed steps
- 🔄 Blue info messages for current step
- ❌ Red errors for failed operations
- ⚠️ Yellow warnings for issues

---

## 💡 Pro Tips

### Efficiency:
- Use cache to avoid re-auditing same sites
- Start with small page limits for unknown sites
- Use interactive mode for client demonstrations

### Accuracy:
- Include protocol in URLs (https://)
- Check robots.txt before large audits
- Monitor logs for analysis accuracy

### Performance:
- Clear cache periodically to free storage
- Use appropriate page limits for site size
- Monitor system resources during large audits

### Troubleshooting:
- Check logs for detailed error information
- Use field test suite to validate setup
- Review manual for comprehensive guidance

---

*For complete documentation, run: `python cli.py manual`*