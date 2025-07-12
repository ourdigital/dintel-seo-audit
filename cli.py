#!/usr/bin/env python3
"""
SEO Audit CLI Tool

A sophisticated command-line interface for managing SEO audits with advanced features
including interactive mode, batch processing, caching, and server management.
"""

import argparse
import sys
import os
import json
import time
import signal
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
import sqlite3
import hashlib

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import SEO audit modules
from src.main import app
from src.models.seo_data import db, Website, Page, Keyword, Link, TechnicalSEO
from src.crawler.seo_crawler import SEOCrawler
from src.crawler.data_importer import SEODataImporter
from src.analyzer.text_analyzer import TextAnalyzer
from src.analyzer.technical_seo_checker import TechnicalSEOChecker
from src.analyzer.page_ranker import PageRanker
from src.analyzer.onpage_seo_analyzer import OnPageSEOAnalyzer
from src.report.report_generator import ReportGenerator
from src.presentation.presentation_designer import PresentationDesigner

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class SEOAuditCLI:
    """Main CLI class for SEO audit operations"""
    
    def __init__(self):
        self.cache_db = self._init_cache_db()
        self.server_process = None
        
    def _init_cache_db(self):
        """Initialize cache database for storing audit results"""
        cache_dir = Path.home() / '.seo_audit'
        cache_dir.mkdir(exist_ok=True)
        cache_db = cache_dir / 'cache.db'
        
        # Create cache database
        conn = sqlite3.connect(str(cache_db))
        conn.execute('''
            CREATE TABLE IF NOT EXISTS audit_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                url_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                report_data TEXT,
                file_paths TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
        return str(cache_db)
    
    def _get_url_hash(self, url):
        """Generate hash for URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _validate_url(self, url):
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _print_header(self, title):
        """Print formatted header"""
        print(f"\n{Colors.HEADER}{'='*50}{Colors.ENDC}")
        print(f"{Colors.HEADER}{title.center(50)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}\n")
    
    def _print_success(self, message):
        """Print success message"""
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
    
    def _print_warning(self, message):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
    
    def _print_error(self, message):
        """Print error message"""
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
    
    def _print_info(self, message):
        """Print info message"""
        print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")
    
    def interactive_mode(self):
        """Interactive CLI mode with guided prompts"""
        self._print_header("SEO Audit Interactive Mode")
        
        # Welcome message
        print(f"{Colors.OKBLUE}Welcome to the SEO Audit CLI Tool!{Colors.ENDC}")
        print("This interactive mode will guide you through the audit process.\n")
        
        # URL input
        while True:
            url = input(f"{Colors.OKCYAN}Enter website URL: {Colors.ENDC}").strip()
            if not url:
                self._print_error("URL cannot be empty")
                continue
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            if self._validate_url(url):
                break
            else:
                self._print_error("Invalid URL format. Please try again.")
        
        # Check cache
        cached_result = self._check_cache(url)
        if cached_result:
            print(f"\n{Colors.WARNING}Found cached result for this URL (created: {cached_result['created_at']}){Colors.ENDC}")
            use_cache = input(f"{Colors.OKCYAN}Use cached result? (y/n): {Colors.ENDC}").strip().lower()
            if use_cache == 'y':
                return self._display_cached_result(cached_result)
        
        # Crawl configuration
        print(f"\n{Colors.OKBLUE}Configure crawl settings:{Colors.ENDC}")
        
        # Max pages
        while True:
            try:
                max_pages = input(f"{Colors.OKCYAN}Max pages to crawl (default: 50): {Colors.ENDC}").strip()
                max_pages = int(max_pages) if max_pages else 50
                if max_pages > 0:
                    break
                else:
                    self._print_error("Max pages must be greater than 0")
            except ValueError:
                self._print_error("Please enter a valid number")
        
        # Max depth
        while True:
            try:
                max_depth = input(f"{Colors.OKCYAN}Max crawl depth (default: 3): {Colors.ENDC}").strip()
                max_depth = int(max_depth) if max_depth else 3
                if max_depth > 0:
                    break
                else:
                    self._print_error("Max depth must be greater than 0")
            except ValueError:
                self._print_error("Please enter a valid number")
        
        # Output format
        print(f"\n{Colors.OKBLUE}Select output formats:{Colors.ENDC}")
        print("1. HTML presentation")
        print("2. PPTX presentation")
        print("3. PDF report")
        print("4. All formats")
        
        while True:
            try:
                format_choice = input(f"{Colors.OKCYAN}Choose format (1-4, default: 4): {Colors.ENDC}").strip()
                format_choice = int(format_choice) if format_choice else 4
                if 1 <= format_choice <= 4:
                    break
                else:
                    self._print_error("Please choose a number between 1 and 4")
            except ValueError:
                self._print_error("Please enter a valid number")
        
        formats = {
            1: ['html'],
            2: ['pptx'],
            3: ['pdf'],
            4: ['html', 'pptx', 'pdf']
        }
        
        selected_formats = formats[format_choice]
        
        # Confirm settings
        print(f"\n{Colors.OKBLUE}Audit Configuration:{Colors.ENDC}")
        print(f"  URL: {url}")
        print(f"  Max Pages: {max_pages}")
        print(f"  Max Depth: {max_depth}")
        print(f"  Output Formats: {', '.join(selected_formats)}")
        
        confirm = input(f"\n{Colors.OKCYAN}Start audit? (y/n): {Colors.ENDC}").strip().lower()
        if confirm != 'y':
            print("Audit cancelled.")
            return
        
        # Start audit
        return self._run_audit(url, max_pages, max_depth, selected_formats)
    
    def _check_cache(self, url):
        """Check if URL has cached results"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM audit_cache WHERE url = ? AND status = 'completed'",
            (url,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'url': result[1],
                'created_at': result[3],
                'report_data': json.loads(result[6]) if result[6] else None,
                'file_paths': json.loads(result[7]) if result[7] else None
            }
        return None
    
    def _display_cached_result(self, cached_result):
        """Display cached audit result"""
        self._print_header("Cached Audit Result")
        
        if cached_result['report_data']:
            data = cached_result['report_data']
            print(f"Website: {data.get('website', 'N/A')}")
            print(f"Overall Score: {data.get('scores', {}).get('overall', 'N/A')}")
            print(f"Technical SEO: {data.get('scores', {}).get('technical', 'N/A')}")
            print(f"On-Page SEO: {data.get('scores', {}).get('onpage', 'N/A')}")
            
            if cached_result['file_paths']:
                paths = cached_result['file_paths']
                print(f"\nGenerated Files:")
                for format_type, path in paths.items():
                    if os.path.exists(path):
                        print(f"  {format_type.upper()}: {path}")
        
        return True
    
    def _run_audit(self, url, max_pages, max_depth, formats):
        """Run complete SEO audit"""
        self._print_header("Starting SEO Audit")
        
        # Store in cache
        url_hash = self._get_url_hash(url)
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO audit_cache (url, url_hash, status) VALUES (?, ?, ?)",
            (url, url_hash, 'running')
        )
        conn.commit()
        conn.close()
        
        try:
            # Initialize Flask app context
            with app.app_context():
                db.create_all()
                
                # Step 1: Crawling
                self._print_info("Step 1/8: Crawling website...")
                crawler = SEOCrawler(url, max_pages=max_pages, max_depth=max_depth)
                crawl_result = crawler.crawl()
                
                if not crawl_result or not crawl_result.get('pages'):
                    self._print_error("No pages found during crawling")
                    return False
                
                self._print_success(f"Found {len(crawl_result['pages'])} pages")
                
                # Step 2: Data import
                self._print_info("Step 2/8: Importing data...")
                importer = SEODataImporter(db)
                
                # Create temporary file for crawl result
                temp_file = f"/tmp/crawl_result_{url_hash}.json"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(crawl_result, f, ensure_ascii=False, indent=2)
                
                import_summary = importer.import_from_json(temp_file)
                self._print_success("Data imported successfully")
                
                # Get website ID
                website = Website.query.filter_by(url=url).first()
                if not website:
                    normalized_url = url.rstrip('/') + '/'
                    website = Website.query.filter_by(url=normalized_url).first()
                
                if not website:
                    self._print_error("Website not found in database")
                    return False
                
                website_id = website.id
                
                # Step 3: Text analysis
                self._print_info("Step 3/8: Analyzing text content...")
                analyzer = TextAnalyzer(db)
                text_analysis = analyzer.analyze_website(website_id)
                self._print_success("Text analysis completed")
                
                # Step 4: Technical SEO
                self._print_info("Step 4/8: Checking technical SEO...")
                tech_checker = TechnicalSEOChecker(db)
                tech_results = tech_checker.check_website(website_id)
                self._print_success("Technical SEO analysis completed")
                
                # Step 5: Page ranking
                self._print_info("Step 5/8: Ranking pages...")
                ranker = PageRanker(db)
                ranked_pages = ranker.rank_pages(website_id, top_n=20)
                self._print_success(f"Ranked {len(ranked_pages)} pages")
                
                # Step 6: On-page SEO
                self._print_info("Step 6/8: Analyzing on-page SEO...")
                page_ids = [page['id'] for page in ranked_pages]
                onpage_analyzer = OnPageSEOAnalyzer(db)
                onpage_results = onpage_analyzer.analyze_pages(page_ids)
                self._print_success("On-page SEO analysis completed")
                
                # Step 7: Report generation
                self._print_info("Step 7/8: Generating reports...")
                report_dir = Path.home() / '.seo_audit' / 'reports' / url_hash
                report_dir.mkdir(parents=True, exist_ok=True)
                
                report_generator = ReportGenerator(db)
                report_files = report_generator.generate_report(
                    website_id,
                    tech_results,
                    ranked_pages,
                    onpage_results,
                    str(report_dir)
                )
                self._print_success("Reports generated")
                
                # Step 8: Presentation design
                self._print_info("Step 8/8: Creating presentations...")
                
                # Load report data
                with open(report_files['json'], 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                charts_dir = report_dir / 'charts'
                charts_dir.mkdir(exist_ok=True)
                
                presentation_dir = report_dir / 'presentations'
                presentation_dir.mkdir(exist_ok=True)
                
                designer = PresentationDesigner(report_data)
                generated_files = {}
                
                # Generate charts
                charts = designer.generate_charts(str(charts_dir))
                
                # Generate requested formats
                if 'html' in formats:
                    html_file = presentation_dir / 'presentation.html'
                    designer.generate_presentation_html(charts, str(html_file))
                    generated_files['html'] = str(html_file)
                    self._print_success(f"HTML presentation: {html_file}")
                
                if 'pptx' in formats:
                    pptx_file = presentation_dir / 'presentation.pptx'
                    designer.generate_pptx(charts, str(pptx_file))
                    generated_files['pptx'] = str(pptx_file)
                    self._print_success(f"PPTX presentation: {pptx_file}")
                
                if 'pdf' in formats:
                    pdf_file = presentation_dir / 'presentation.pdf'
                    if 'html' in generated_files:
                        designer.generate_pdf(generated_files['html'], str(pdf_file))
                        generated_files['pdf'] = str(pdf_file)
                        self._print_success(f"PDF report: {pdf_file}")
                
                # Update cache
                conn = sqlite3.connect(self.cache_db)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE audit_cache SET status = ?, report_data = ?, file_paths = ?, updated_at = CURRENT_TIMESTAMP WHERE url = ?",
                    ('completed', json.dumps(report_data), json.dumps(generated_files), url)
                )
                conn.commit()
                conn.close()
                
                # Display summary
                self._print_header("Audit Complete!")
                print(f"Website: {report_data.get('website', url)}")
                print(f"Overall Score: {report_data.get('scores', {}).get('overall', 'N/A')}/100")
                print(f"Technical SEO: {report_data.get('scores', {}).get('technical', 'N/A')}/100")
                print(f"On-Page SEO: {report_data.get('scores', {}).get('onpage', 'N/A')}/100")
                print(f"\nGenerated Files:")
                for format_type, path in generated_files.items():
                    print(f"  {format_type.upper()}: {path}")
                
                # Clean up
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                return True
                
        except Exception as e:
            self._print_error(f"Audit failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def quick_audit(self, url, max_pages=50, max_depth=3):
        """Quick audit without interactive prompts"""
        self._print_header("Quick SEO Audit")
        
        if not self._validate_url(url):
            self._print_error("Invalid URL format")
            return False
        
        return self._run_audit(url, max_pages, max_depth, ['html', 'pptx', 'pdf'])
    
    def list_cache(self):
        """List cached audit results"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        cursor.execute("SELECT url, created_at, status FROM audit_cache ORDER BY created_at DESC")
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            self._print_info("No cached audits found")
            return
        
        self._print_header("Cached Audits")
        for url, created_at, status in results:
            status_icon = "✅" if status == 'completed' else "🔄" if status == 'running' else "❌"
            print(f"{status_icon} {url} (Created: {created_at})")
    
    def clear_cache(self):
        """Clear all cached results"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM audit_cache")
        conn.commit()
        conn.close()
        
        self._print_success("Cache cleared")
    
    def start_server(self, host='localhost', port=5001):
        """Start the Flask web server"""
        self._print_header("Starting SEO Audit Server")
        
        # Check if port is available
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex((host, port)) == 0:
                self._print_error(f"Port {port} is already in use")
                return False
        
        try:
            self._print_info(f"Starting server on {host}:{port}")
            
            # Start server process
            cmd = [sys.executable, 'src/main.py']
            env = os.environ.copy()
            env['FLASK_HOST'] = host
            env['FLASK_PORT'] = str(port)
            
            self.server_process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Wait for server to start
            time.sleep(3)
            
            if self.server_process.poll() is None:
                self._print_success(f"Server started successfully!")
                self._print_info(f"Access the web interface at: http://{host}:{port}")
                self._print_info("Press Ctrl+C to stop the server")
                
                # Monitor server
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self._print_info("Stopping server...")
                    self.server_process.terminate()
                    self.server_process.wait()
                    self._print_success("Server stopped")
                    return True
            else:
                self._print_error("Failed to start server")
                return False
                
        except Exception as e:
            self._print_error(f"Error starting server: {str(e)}")
            return False
    
    def stop_server(self):
        """Stop the Flask web server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self._print_success("Server stopped")
        else:
            self._print_info("No server process found")
            
    def show_manual(self):
        """Display the comprehensive user manual"""
        manual_file = Path(__file__).parent / 'CLI_USER_MANUAL.md'
        
        if manual_file.exists():
            try:
                with open(manual_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Try to use a pager if available, otherwise print directly
                try:
                    import subprocess
                    subprocess.run(['less', str(manual_file)], check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    try:
                        subprocess.run(['more', str(manual_file)], check=True)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        # Fallback to direct print
                        print(content)
                        
            except Exception as e:
                self._print_error(f"Could not display manual: {e}")
                self._print_info("Manual file location: CLI_USER_MANUAL.md")
        else:
            self._print_error("User manual not found")
            self._print_info("Please ensure CLI_USER_MANUAL.md exists in the same directory")
            
    def show_quick_help(self):
        """Display quick reference help"""
        self._print_header("SEO Audit CLI - Quick Reference")
        
        print(f"{Colors.OKBLUE}🚀 GETTING STARTED{Colors.ENDC}")
        print("  python cli.py --interactive           # Best for beginners")
        print("  python cli.py audit --url site.com    # Quick audit")
        print()
        
        print(f"{Colors.OKBLUE}📋 MAIN COMMANDS{Colors.ENDC}")
        print("  --interactive, -i     Start guided audit mode")
        print("  audit                 Run SEO audit")
        print("  server                Start/stop web interface")
        print("  cache                 Manage cached results")
        print("  history               View audit history")
        print()
        
        print(f"{Colors.OKBLUE}💡 QUICK EXAMPLES{Colors.ENDC}")
        print("  python cli.py audit --url https://example.com --max-pages 20")
        print("  python cli.py server --port 8080")
        print("  python cli.py cache --list")
        print("  python cli.py cache --clear")
        print()
        
        print(f"{Colors.OKBLUE}📖 MORE HELP{Colors.ENDC}")
        print("  python cli.py --help              # Full help")
        print("  python cli.py [command] --help    # Command-specific help")
        print("  python cli.py manual              # Comprehensive user manual")
        print()
        
        print(f"{Colors.OKBLUE}📁 OUTPUT LOCATIONS{Colors.ENDC}")
        print("  Reports: ~/.seo_audit/reports/")
        print("  Cache:   ~/.seo_audit/cache.db")
        print("  Logs:    seo_audit.log")
        print()

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='''
SEO Audit CLI Tool - Comprehensive website SEO analysis with professional reporting

This tool performs complete SEO audits including technical SEO, on-page optimization,
keyword analysis, and generates professional presentations in HTML, PPTX, and PDF formats.
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
COMMANDS:
  Interactive Mode:
    %(prog)s --interactive              # Guided audit with prompts
    %(prog)s -i                         # Short form
    
  Direct Audit:
    %(prog)s audit --url https://example.com           # Basic audit (50 pages, depth 3)
    %(prog)s audit -u https://site.com -p 25 -d 2     # Custom limits
    %(prog)s audit --url https://site.com --interactive # Guided audit for specific URL
    
  Server Management:
    %(prog)s server                     # Start web server (localhost:5001)
    %(prog)s server --host 0.0.0.0 --port 8080        # Custom host/port
    %(prog)s server --stop              # Stop server
    
  Cache Management:
    %(prog)s cache --list               # View cached audits
    %(prog)s cache --clear              # Clear all cache
    %(prog)s cache -l                   # Short form
    
  History & Monitoring:
    %(prog)s history                    # View audit history
    %(prog)s history --website example.com             # Filter by site

USAGE PATTERNS:
  New Users:        %(prog)s --interactive
  Quick Audit:      %(prog)s audit --url https://your-site.com
  Web Interface:    %(prog)s server (then visit http://localhost:5001)
  Batch Work:       %(prog)s audit --url site1.com && %(prog)s audit --url site2.com
  
OUTPUT:
  All audits generate HTML presentations, PPTX slides, and PDF reports.
  Files are saved to ~/.seo_audit/reports/ and cached for future reference.
  
PERFORMANCE:
  Small sites (1-10 pages):    1-5 minutes
  Medium sites (10-50 pages):  5-15 minutes  
  Large sites (50+ pages):     15+ minutes
  
For detailed help: See CLI_USER_MANUAL.md or %(prog)s [command] --help
        '''
    )
    
    # Global options
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Start interactive mode')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Audit command
    audit_parser = subparsers.add_parser(
        'audit', 
        help='Run comprehensive SEO audit',
        description='''
Run a complete 8-step SEO audit including:
• Website crawling and content extraction
• Technical SEO analysis (robots.txt, sitemap, Core Web Vitals)
• On-page SEO evaluation (meta tags, headings, content)
• Keyword analysis and density calculation
• Page ranking and prioritization
• Professional report generation (HTML, PPTX, PDF)

The audit typically takes 1-30 minutes depending on site size.
        ''',
        epilog='''
Examples:
  %(prog)s --url https://example.com                    # Basic audit
  %(prog)s --url https://site.com --max-pages 25       # Limit to 25 pages
  %(prog)s --url https://site.com --max-depth 2        # Shallow crawl
  %(prog)s --url https://site.com --interactive        # Guided setup
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    audit_parser.add_argument('--url', '-u', required=True, 
                             help='Website URL to audit (include https://)')
    audit_parser.add_argument('--max-pages', '-p', type=int, default=50,
                             help='Maximum pages to crawl (1-1000, default: 50)')
    audit_parser.add_argument('--max-depth', '-d', type=int, default=3,
                             help='Maximum crawl depth from homepage (1-10, default: 3)')
    audit_parser.add_argument('--interactive', action='store_true',
                             help='Use interactive mode for guided configuration')
    
    # Server command
    server_parser = subparsers.add_parser(
        'server', 
        help='Manage web server interface',
        description='''
Start or stop the Flask web server that provides a browser-based interface
for SEO audits. The web interface offers the same functionality as the CLI
but with a user-friendly graphical interface.

The server runs until stopped with Ctrl+C or the --stop flag.
        ''',
        epilog='''
Examples:
  %(prog)s                                    # Start on localhost:5001
  %(prog)s --port 8080                       # Custom port
  %(prog)s --host 0.0.0.0 --port 8080       # Public access
  %(prog)s --stop                           # Stop running server
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    server_parser.add_argument('--host', default='localhost',
                              help='Server host address (default: localhost)')
    server_parser.add_argument('--port', '-p', type=int, default=5001,
                              help='Server port number (default: 5001)')
    server_parser.add_argument('--stop', action='store_true',
                              help='Stop the running server gracefully')
    
    # Cache command
    cache_parser = subparsers.add_parser(
        'cache', 
        help='Manage audit cache and storage',
        description='''
Manage the local cache of audit results. The cache stores completed audits
in ~/.seo_audit/cache.db to avoid re-auditing the same sites unnecessarily.

Each cached audit includes the full report data and can be reused when
auditing the same URL again.
        ''',
        epilog='''
Examples:
  %(prog)s --list                            # Show all cached audits
  %(prog)s -l                                # Short form
  %(prog)s --clear                           # Remove all cached data
  %(prog)s -c                                # Short form for clear
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    cache_parser.add_argument('--list', '-l', action='store_true',
                             help='Display all cached audits with dates and status')
    cache_parser.add_argument('--clear', '-c', action='store_true',
                             help='Remove all cached audit data (frees storage)')
    
    # History command
    history_parser = subparsers.add_parser(
        'history', 
        help='View audit history and trends',
        description='''
View historical audit data and track changes over time. This helps monitor
SEO improvements and identify trends in website performance.
        ''',
        epilog='''
Examples:
  %(prog)s                                   # Show all audit history
  %(prog)s --website example.com            # Filter by specific site
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    history_parser.add_argument('--website', '-w', 
                               help='Filter history by website domain')
                               
    # Manual command
    manual_parser = subparsers.add_parser(
        'manual',
        help='Show comprehensive user manual',
        description='Display the complete user manual with detailed explanations and examples'
    )
    
    # Help command
    help_parser = subparsers.add_parser(
        'help',
        help='Show quick reference guide',
        description='Display quick reference help with common commands and examples'
    )
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = SEOAuditCLI()
    
    # Handle commands
    if args.interactive or (not args.command and len(sys.argv) == 1):
        cli.interactive_mode()
    elif args.command == 'audit':
        if args.interactive:
            cli.interactive_mode()
        else:
            cli.quick_audit(args.url, args.max_pages, args.max_depth)
    elif args.command == 'server':
        if args.stop:
            cli.stop_server()
        else:
            cli.start_server(args.host, args.port)
    elif args.command == 'cache':
        if args.list:
            cli.list_cache()
        elif args.clear:
            cli.clear_cache()
    elif args.command == 'history':
        cli.list_cache()  # For now, same as cache list
    elif args.command == 'manual':
        cli.show_manual()
    elif args.command == 'help':
        cli.show_quick_help()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()