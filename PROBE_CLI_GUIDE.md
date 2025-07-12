# Probe CLI - Enterprise SEO Audit Toolkit

## 🚀 Installation

```bash
# Install probe command system-wide
python install.py

# Or run directly
python probe.py --help
```

## 📋 Command Structure

### Quick Usage
```bash
# Direct URL analysis (simplest)
probe https://example.com

# Equivalent to
probe seo https://example.com
```

### Full Command Structure
```
probe [global-options] <command> [command-options] [arguments]
```

---

## 🎯 Commands Overview

| Command | Purpose | Example |
|---------|---------|---------|
| `seo` | SEO analysis and audit | `probe seo https://site.com` |
| `server` | Web interface management | `probe server start` |
| `cache` | Cache management | `probe cache list` |
| `report` | Report generation | `probe report list` |
| `config` | Configuration management | `probe config show` |

---

## 📖 Detailed Commands

### SEO Command
**Purpose**: Comprehensive SEO audit and analysis

```bash
# Basic syntax
probe seo [URL] [options]

# Examples
probe seo https://example.com                    # Basic audit
probe seo https://site.com -d 3 -p 100          # Deep analysis (3 levels, 100 pages)
probe seo --interactive                          # Guided mode
probe seo --batch sites.txt -f pdf html         # Batch processing
probe seo https://site.com --no-cache           # Force fresh analysis
probe seo https://site.com -l ko                # Korean language analysis
```

**Options:**
- `url` - Target URL to analyze (positional)
- `-i, --interactive` - Launch interactive mode with prompts
- `-b, --batch FILE` - Process multiple URLs from file
- `-d, --depth N` - Crawl depth (default: 2)
- `-p, --pages N` - Maximum pages to crawl (default: 50)
- `-f, --format FORMAT` - Output format(s): json, markdown, html, pdf, pptx
- `-o, --output PATH` - Output directory or file path
- `--no-cache` - Disable caching, force fresh analysis
- `-l, --language LANG` - Content language: auto, ko, en

**What it does:**
- ✅ 8-step comprehensive SEO audit
- ✅ Technical SEO analysis (robots.txt, sitemap, Core Web Vitals)
- ✅ On-page SEO evaluation (meta tags, headings, content)
- ✅ Keyword analysis and density calculation
- ✅ Multi-language content analysis
- ✅ Professional report generation in multiple formats
- ✅ Intelligent caching for efficiency

---

### Server Command
**Purpose**: Web interface server management

```bash
# Start server
probe server start [options]
probe server start -p 8080 --host 0.0.0.0      # Custom host/port
probe server start --debug                      # Debug mode

# Server management
probe server stop                               # Stop server
probe server status                             # Check status
```

**Sub-commands:**
- `start` - Start the web server
  - `-p, --port N` - Port number (default: 5000)
  - `--host HOST` - Host address (default: 127.0.0.1)
  - `--debug` - Enable debug mode
- `stop` - Stop the web server
- `status` - Check server status

**What it does:**
- ✅ Launches Flask web interface
- ✅ Provides browser-based SEO audit interface
- ✅ Handles multiple simultaneous users
- ✅ Graceful server management

---

### Cache Command
**Purpose**: Audit cache and storage management

```bash
# List cached audits
probe cache list                                # Show recent 20
probe cache list -l 50                         # Show recent 50

# Clear cache
probe cache clear --all                        # Clear everything
probe cache clear --older-than 7              # Clear >7 days old

# Cache information
probe cache info                               # Statistics
```

**Sub-commands:**
- `list` - List cached audits
  - `-l, --limit N` - Maximum results to show (default: 20)
- `clear` - Clear cache data
  - `--all` - Clear all cached data
  - `--older-than DAYS` - Clear cache older than N days
- `info` - Show cache statistics

**What it does:**
- ✅ SQLite-based cache management
- ✅ Storage optimization and cleanup
- ✅ Audit history tracking
- ✅ Efficient result reuse

---

### Report Command
**Purpose**: Report generation from existing audits

```bash
# List available reports
probe report list

# Generate specific report
probe report abc123 -f pdf -o ./report.pdf
probe report abc123 --format html             # HTML format
```

**Options:**
- `audit_id` - Audit ID to generate report for (positional)
- `-l, --list` - List available audit reports
- `-f, --format FORMAT` - Report format: json, markdown, html, pdf, pptx
- `-o, --output PATH` - Output file path

**What it does:**
- ✅ Lists completed audits available for reporting
- ✅ Regenerates reports in different formats
- ✅ Custom output file naming
- ✅ Professional presentation quality

---

### Config Command
**Purpose**: Tool configuration management

```bash
# View configuration
probe config show

# Set configuration values
probe config set default_depth 3
probe config set default_pages 100
probe config set default_host 0.0.0.0

# Reset to defaults
probe config reset
```

**Sub-commands:**
- `show` - Display current configuration
- `set KEY VALUE` - Set configuration value
- `reset` - Reset to default configuration

**Available Settings:**
- `default_depth` - Default crawl depth (2)
- `default_pages` - Default max pages (50)
- `default_host` - Default server host (127.0.0.1)
- `default_port` - Default server port (5000)
- `default_format` - Default output formats (["json"])
- `cache_retention_days` - Cache retention period (30)
- `verbose` - Verbose output (false)
- `language` - Default language (auto)

---

## 🌟 Global Options

Available with any command:

```bash
probe --version                                # Show version
probe --verbose seo https://site.com           # Verbose output
probe --config custom.yaml seo https://site.com # Custom config file
```

**Options:**
- `-v, --version` - Show version information
- `-V, --verbose` - Enable verbose output
- `-c, --config FILE` - Use custom configuration file

---

## 🎯 Usage Patterns

### For Beginners
```bash
# Start here
probe --help
probe seo --interactive
probe https://your-site.com                    # Quick test
```

### For SEO Professionals
```bash
# Client workflow
probe seo client-site.com -d 3 -p 75          # Comprehensive audit
probe cache list                               # Review history
probe report list                              # Available reports
```

### For Developers
```bash
# Testing pipeline
probe seo staging.site.com -p 10 --no-cache
probe seo production.site.com -f json -o ./results/
probe cache clear --older-than 1              # Cleanup
```

### For Agencies
```bash
# Client presentations
probe server start -p 8080                    # Web interface
probe seo --batch client-sites.txt -f pptx    # Batch reports
probe config set default_format '["pdf", "pptx"]'  # Agency defaults
```

### For Content Teams
```bash
# Regular monitoring
probe seo blog.company.com -p 25
probe cache list                               # Track improvements
probe seo blog.company.com --no-cache         # Fresh analysis
```

---

## 📊 Output and File Management

### Default File Locations
- **Reports**: `~/.seo_audit/reports/[site-hash]/`
- **Cache**: `~/.probe/cache.db`
- **Config**: `~/.probe/config.json`
- **Logs**: `seo_audit.log`, `seo_audit_errors.log`

### Output Formats
- **JSON**: Structured data for integration
- **Markdown**: Human-readable text reports
- **HTML**: Interactive presentations with navigation
- **PDF**: Professional print-ready documents
- **PPTX**: PowerPoint presentations for meetings

---

## ⚡ Performance Guidelines

### Recommended Settings by Site Type

| Site Type | Command | Time |
|-----------|---------|------|
| **Small Business** | `probe seo site.com -p 15 -d 2` | 3-8 min |
| **Blog/Content** | `probe seo site.com -p 30 -d 3` | 8-15 min |
| **E-commerce** | `probe seo site.com -p 75 -d 2` | 15-30 min |
| **Enterprise** | `probe seo site.com -p 150 -d 3` | 30-60 min |

### Resource Usage
- **Memory**: 200MB - 1GB depending on site complexity
- **Storage**: 5-20MB per audit cache
- **Network**: 10-100MB depending on page content

---

## 🔧 Advanced Features

### Batch Processing
Create a file `sites.txt`:
```
https://site1.com
https://site2.com
https://site3.com
# Comments are supported
```

Then run:
```bash
probe seo --batch sites.txt -f pdf html -o ./batch-reports/
```

### Configuration Management
```bash
# Set up agency defaults
probe config set default_depth 3
probe config set default_pages 75
probe config set default_format '["html", "pdf", "pptx"]'

# All future audits use these settings
probe seo client1.com
probe seo client2.com
```

### Cache Optimization
```bash
# Weekly cleanup
probe cache clear --older-than 7

# Storage monitoring
probe cache info

# Force fresh analysis
probe seo site.com --no-cache
```

---

## 🚨 Troubleshooting

### Common Issues

**Command not found: probe**
```bash
# If installed via install.py, check PATH
echo $PATH | grep -q ~/.local/bin || echo "Add ~/.local/bin to PATH"

# Or run directly
python probe.py --help
```

**URL format errors**
```bash
# ❌ Wrong
probe seo example.com

# ✅ Correct  
probe seo https://example.com
```

**Port conflicts**
```bash
# ❌ Error: Address already in use
probe server start

# ✅ Solution: Different port
probe server start -p 8080
```

**Cache issues**
```bash
# Clear problematic cache
probe cache clear --all

# Check cache status
probe cache info
```

### Getting Help
```bash
probe --help                    # Main help
probe seo --help                # SEO command help
probe server start --help       # Server start help
probe cache --help              # Cache management help
```

---

## 🎉 Migration from Old CLI

### Command Mapping

| Old Command | New Command |
|-------------|-------------|
| `python cli.py --interactive` | `probe seo --interactive` |
| `python cli.py audit --url site.com` | `probe seo site.com` |
| `python cli.py server --port 8080` | `probe server start -p 8080` |
| `python cli.py cache --list` | `probe cache list` |
| `python cli.py cache --clear` | `probe cache clear --all` |

### Benefits of New Structure
- ✅ **Simpler**: No need for `python` or file names
- ✅ **Professional**: Industry-standard CLI patterns
- ✅ **Intuitive**: Logical command grouping
- ✅ **Powerful**: More options and flexibility
- ✅ **Configurable**: Persistent settings
- ✅ **Scalable**: Easy to extend with new features

Your SEO audit tool is now enterprise-ready with a professional CLI interface!