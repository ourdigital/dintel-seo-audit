#!/usr/bin/env python3
"""
probe - Enterprise SEO Audit Toolkit CLI
A professional command-line interface for comprehensive website SEO analysis
"""

import argparse
import sys
import os
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import subprocess
import sqlite3
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import existing modules
from cli import SEOAuditCLI, Colors

# Optional performance monitor import
try:
    from performance_monitor import PerformanceMonitor
except ImportError:
    PerformanceMonitor = None

class ProbeConfig:
    """Configuration management for probe CLI"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.probe'
        self.config_file = self.config_dir / 'config.json'
        self.config_dir.mkdir(exist_ok=True)
        self.default_config = {
            'default_depth': 2,
            'default_pages': 50,
            'default_host': '127.0.0.1',
            'default_port': 5000,
            'default_format': ['json'],
            'cache_retention_days': 30,
            'verbose': False,
            'language': 'auto'
        }
        
    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for missing keys
                merged_config = self.default_config.copy()
                merged_config.update(config)
                return merged_config
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
                return self.default_config.copy()
        return self.default_config.copy()
        
    def save(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get(self, key: str, default=None):
        """Get configuration value"""
        config = self.load()
        return config.get(key, default)
        
    def set(self, key: str, value: Any):
        """Set configuration value"""
        config = self.load()
        config[key] = value
        self.save(config)
        
    def reset(self):
        """Reset to default configuration"""
        self.save(self.default_config.copy())

def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser for probe command."""
    
    parser = argparse.ArgumentParser(
        prog='probe',
        description='Enterprise SEO Audit Toolkit - Comprehensive website analysis and reporting',
        epilog='For more information on each command, use: probe <command> --help',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global options
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='probe 1.0.0 - Enterprise SEO Audit Toolkit'
    )
    
    parser.add_argument(
        '--verbose', '-V',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='<command>'
    )
    
    # =================== SEO COMMAND ===================
    seo_parser = subparsers.add_parser(
        'seo',
        help='SEO analysis and audit',
        description='Comprehensive SEO audit with technical, on-page, and content analysis',
        epilog='''
Examples:
  probe seo https://example.com                    # Basic audit
  probe seo https://site.com -d 3 -p 100          # Deep analysis
  probe seo --interactive                          # Guided mode
  probe seo --batch sites.txt -f pdf html         # Batch processing
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    seo_parser.add_argument(
        'url',
        nargs='?',
        help='Target URL to analyze'
    )
    
    seo_parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Launch interactive mode with guided prompts'
    )
    
    seo_parser.add_argument(
        '--batch', '-b',
        type=str,
        metavar='FILE',
        help='Batch process URLs from file'
    )
    
    seo_parser.add_argument(
        '--depth', '-d',
        type=int,
        metavar='N',
        help='Crawl depth (default: 2)'
    )
    
    seo_parser.add_argument(
        '--pages', '-p',
        type=int,
        metavar='N',
        help='Maximum pages to crawl (default: 50)'
    )
    
    seo_parser.add_argument(
        '--format', '-f',
        choices=['json', 'markdown', 'html', 'pdf', 'pptx'],
        nargs='+',
        help='Output format(s) (default: json)'
    )
    
    seo_parser.add_argument(
        '--output', '-o',
        type=str,
        metavar='PATH',
        help='Output directory or file path'
    )
    
    seo_parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable caching and force fresh analysis'
    )
    
    seo_parser.add_argument(
        '--language', '-l',
        choices=['auto', 'ko', 'en'],
        help='Content language for analysis (default: auto)'
    )
    
    # =================== SERVER COMMAND ===================
    server_parser = subparsers.add_parser(
        'server',
        help='Web server management',
        description='Start, stop, or check status of the web interface server'
    )
    
    server_subparsers = server_parser.add_subparsers(
        dest='server_action',
        help='Server actions',
        metavar='<action>'
    )
    
    # Server start
    start_parser = server_subparsers.add_parser('start', help='Start the web server')
    start_parser.add_argument(
        '--port', '-p',
        type=int,
        help='Port number (default: 5000)'
    )
    start_parser.add_argument(
        '--host',
        type=str,
        help='Host address (default: 127.0.0.1)'
    )
    start_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    # Server stop
    server_subparsers.add_parser('stop', help='Stop the web server')
    
    # Server status
    server_subparsers.add_parser('status', help='Check server status')
    
    # =================== CACHE COMMAND ===================
    cache_parser = subparsers.add_parser(
        'cache',
        help='Cache management',
        description='Manage audit cache and stored results'
    )
    
    cache_subparsers = cache_parser.add_subparsers(
        dest='cache_action',
        help='Cache actions',
        metavar='<action>'
    )
    
    # Cache list
    list_parser = cache_subparsers.add_parser('list', help='List cached audits')
    list_parser.add_argument(
        '--limit', '-l',
        type=int,
        default=20,
        help='Maximum number of results to show (default: 20)'
    )
    
    # Cache clear
    clear_parser = cache_subparsers.add_parser('clear', help='Clear cache')
    clear_parser.add_argument(
        '--all',
        action='store_true',
        help='Clear all cached data'
    )
    clear_parser.add_argument(
        '--older-than',
        type=str,
        metavar='DAYS',
        help='Clear cache older than N days'
    )
    
    # Cache info
    cache_subparsers.add_parser('info', help='Show cache statistics')
    
    # =================== REPORT COMMAND ===================
    report_parser = subparsers.add_parser(
        'report',
        help='Report generation and management',
        description='Generate reports from existing audit data'
    )
    
    report_parser.add_argument(
        'audit_id',
        nargs='?',
        help='Audit ID to generate report for'
    )
    
    report_parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available audit reports'
    )
    
    report_parser.add_argument(
        '--format', '-f',
        choices=['json', 'markdown', 'html', 'pdf', 'pptx'],
        default='html',
        help='Report format (default: html)'
    )
    
    report_parser.add_argument(
        '--output', '-o',
        type=str,
        metavar='PATH',
        help='Output file path'
    )
    
    # =================== CONFIG COMMAND ===================
    config_parser = subparsers.add_parser(
        'config',
        help='Configuration management',
        description='View and modify tool configuration'
    )
    
    config_subparsers = config_parser.add_subparsers(
        dest='config_action',
        help='Configuration actions',
        metavar='<action>'
    )
    
    # Config show
    config_subparsers.add_parser('show', help='Show current configuration')
    
    # Config set
    set_parser = config_subparsers.add_parser('set', help='Set configuration value')
    set_parser.add_argument('key', help='Configuration key')
    set_parser.add_argument('value', help='Configuration value')
    
    # Config reset
    config_subparsers.add_parser('reset', help='Reset to default configuration')
    
    return parser


class ProbeApp:
    """Main probe application class"""
    
    def __init__(self):
        self.config = ProbeConfig()
        self.cli = SEOAuditCLI()
        
    def print_status(self, message: str, status: str = "info"):
        """Print colored status message"""
        colors = {
            "info": Colors.OKCYAN,
            "success": Colors.OKGREEN,
            "warning": Colors.WARNING,
            "error": Colors.FAIL
        }
        icon = {
            "info": "🔍",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        color = colors.get(status, Colors.ENDC)
        emoji = icon.get(status, "ℹ️")
        print(f"{color}{emoji} {message}{Colors.ENDC}")
        
    def handle_direct_url(self, url: str) -> bool:
        """Handle direct URL input (no subcommand)"""
        self.print_status(f"Running SEO analysis on: {url}")
        
        # Use default configuration
        config = self.config.load()
        depth = config.get('default_depth', 2)
        pages = config.get('default_pages', 50)
        
        try:
            result = self.cli.quick_audit(url, pages, depth)
            if result:
                self.print_status("SEO analysis completed successfully", "success")
            else:
                self.print_status("SEO analysis failed", "error")
            return result
        except Exception as e:
            self.print_status(f"Error during analysis: {str(e)}", "error")
            return False
    
    def handle_seo_command(self, args):
        """Handle SEO analysis command"""
        config = self.config.load()
        
        # Set defaults from config if not specified
        depth = args.depth if args.depth is not None else config.get('default_depth', 2)
        pages = args.pages if args.pages is not None else config.get('default_pages', 50)
        formats = args.format if args.format else config.get('default_format', ['json'])
        
        # Validate input parameters
        if depth is not None and (depth < 1 or depth > 10):
            self.print_status("Depth must be between 1 and 10", "error")
            return False
            
        if pages is not None and (pages < 1 or pages > 1000):
            self.print_status("Pages must be between 1 and 1000", "error")
            return False
        
        if args.interactive:
            self.print_status("Launching interactive SEO analysis mode...", "info")
            return self.cli.interactive_mode()
            
        elif args.batch:
            self.print_status(f"Starting batch analysis from: {args.batch}", "info")
            return self._handle_batch_analysis(args.batch, depth, pages, formats, args.output)
            
        elif args.url:
            self.print_status(f"Analyzing: {args.url}")
            self.print_status(f"Configuration: Depth={depth}, Pages={pages}, Formats={formats}")
            
            # Handle no-cache option
            if args.no_cache:
                # Clear cache for this specific URL
                self._clear_url_cache(args.url)
                
            try:
                result = self.cli.quick_audit(args.url, pages, depth)
                if result:
                    self.print_status("SEO analysis completed successfully", "success")
                else:
                    self.print_status("SEO analysis failed", "error")
                return result
            except Exception as e:
                self.print_status(f"Error during analysis: {str(e)}", "error")
                return False
        else:
            self.print_status("URL required for SEO analysis", "error")
            self.print_status("Use 'probe seo --help' for more options")
            return False
    
    def _handle_batch_analysis(self, batch_file: str, depth: int, pages: int, formats: List[str], output_dir: str = None):
        """Handle batch processing of URLs"""
        try:
            with open(batch_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
            if not urls:
                self.print_status("No valid URLs found in batch file", "error")
                return False
                
            self.print_status(f"Processing {len(urls)} URLs from batch file")
            
            success_count = 0
            for i, url in enumerate(urls, 1):
                self.print_status(f"[{i}/{len(urls)}] Processing: {url}")
                try:
                    result = self.cli.quick_audit(url, pages, depth)
                    if result:
                        success_count += 1
                        self.print_status(f"✅ Completed: {url}", "success")
                    else:
                        self.print_status(f"❌ Failed: {url}", "error")
                except Exception as e:
                    self.print_status(f"❌ Error processing {url}: {str(e)}", "error")
                    
            self.print_status(f"Batch processing complete: {success_count}/{len(urls)} successful")
            return success_count > 0
            
        except FileNotFoundError:
            self.print_status(f"Batch file not found: {batch_file}", "error")
            return False
        except Exception as e:
            self.print_status(f"Error processing batch file: {str(e)}", "error")
            return False
    
    def _clear_url_cache(self, url: str):
        """Clear cache for specific URL"""
        try:
            conn = sqlite3.connect(self.cli.cache_db)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM audit_cache WHERE url = ?", (url,))
            conn.commit()
            conn.close()
            self.print_status(f"Cleared cache for: {url}")
        except Exception as e:
            self.print_status(f"Warning: Could not clear cache: {str(e)}", "warning")
    
    def handle_server_command(self, args):
        """Handle server management command"""
        config = self.config.load()
        
        if args.server_action == 'start':
            host = args.host if args.host else config.get('default_host', '127.0.0.1')
            port = args.port if args.port else config.get('default_port', 5000)
            self.print_status(f"Starting server on {host}:{port}")
            return self.cli.start_server(host, port)
            
        elif args.server_action == 'stop':
            self.print_status("Stopping server...")
            return self.cli.stop_server()
            
        elif args.server_action == 'status':
            self.print_status("Checking server status...")
            return self._check_server_status()
            
        else:
            self.print_status("Server action required", "error")
            self.print_status("Available actions: start, stop, status")
            return False
    
    def _check_server_status(self):
        """Check if server is running"""
        try:
            import socket
            config = self.config.load()
            host = config.get('default_host', '127.0.0.1')
            port = config.get('default_port', 5000)
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex((host, port))
                if result == 0:
                    self.print_status(f"Server is running on {host}:{port}", "success")
                    return True
                else:
                    self.print_status(f"Server is not running on {host}:{port}", "warning")
                    return False
        except Exception as e:
            self.print_status(f"Error checking server status: {str(e)}", "error")
            return False
    
    def handle_cache_command(self, args):
        """Handle cache management command"""
        if args.cache_action == 'list':
            self.print_status(f"Showing {args.limit} recent cached audits...")
            return self._list_cache(args.limit)
            
        elif args.cache_action == 'clear':
            if args.all:
                self.print_status("Clearing all cached data...")
                return self.cli.clear_cache()
            elif args.older_than:
                self.print_status(f"Clearing cache older than {args.older_than} days...")
                return self._clear_old_cache(int(args.older_than))
            else:
                self.print_status("Specify --all or --older-than option", "error")
                return False
                
        elif args.cache_action == 'info':
            self.print_status("Cache statistics...")
            return self._show_cache_info()
            
        else:
            self.print_status("Cache action required", "error")
            self.print_status("Available actions: list, clear, info")
            return False
    
    def _list_cache(self, limit: int):
        """List cached audits with limit"""
        try:
            conn = sqlite3.connect(self.cli.cache_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT url, created_at, status FROM audit_cache ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                self.print_status("No cached audits found", "warning")
                return True
                
            print(f"\n{Colors.HEADER}Recent Cached Audits:{Colors.ENDC}")
            for url, created_at, status in results:
                status_icon = "✅" if status == 'completed' else "🔄" if status == 'running' else "❌"
                print(f"{status_icon} {url} (Created: {created_at})")
            
            return True
            
        except Exception as e:
            self.print_status(f"Error listing cache: {str(e)}", "error")
            return False
    
    def _clear_old_cache(self, days: int):
        """Clear cache older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
            
            conn = sqlite3.connect(self.cli.cache_db)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM audit_cache WHERE created_at < ?", (cutoff_str,))
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            self.print_status(f"Cleared {deleted_count} cache entries older than {days} days", "success")
            return True
            
        except Exception as e:
            self.print_status(f"Error clearing old cache: {str(e)}", "error")
            return False
    
    def _show_cache_info(self):
        """Show cache statistics"""
        try:
            conn = sqlite3.connect(self.cli.cache_db)
            cursor = conn.cursor()
            
            # Total entries
            cursor.execute("SELECT COUNT(*) FROM audit_cache")
            total_count = cursor.fetchone()[0]
            
            # Status breakdown
            cursor.execute("SELECT status, COUNT(*) FROM audit_cache GROUP BY status")
            status_counts = dict(cursor.fetchall())
            
            # Storage size
            cache_file = Path(self.cli.cache_db)
            file_size = cache_file.stat().st_size if cache_file.exists() else 0
            file_size_mb = file_size / (1024 * 1024)
            
            conn.close()
            
            print(f"\n{Colors.HEADER}Cache Statistics:{Colors.ENDC}")
            print(f"  Total entries: {total_count}")
            print(f"  Database size: {file_size_mb:.2f} MB")
            print(f"  Status breakdown:")
            for status, count in status_counts.items():
                print(f"    {status}: {count}")
            
            return True
            
        except Exception as e:
            self.print_status(f"Error getting cache info: {str(e)}", "error")
            return False
    
    def handle_report_command(self, args):
        """Handle report generation command"""
        if args.list:
            self.print_status("Available audit reports...")
            return self._list_reports()
        elif args.audit_id:
            self.print_status(f"Generating {args.format} report for audit: {args.audit_id}")
            return self._generate_report(args.audit_id, args.format, args.output)
        else:
            self.print_status("Audit ID required or use --list", "error")
            return False
    
    def _list_reports(self):
        """List available reports"""
        try:
            conn = sqlite3.connect(self.cli.cache_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT url_hash, url, created_at, status FROM audit_cache WHERE status = 'completed' ORDER BY created_at DESC"
            )
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                self.print_status("No completed audits found", "warning")
                return True
                
            print(f"\n{Colors.HEADER}Available Reports:{Colors.ENDC}")
            for url_hash, url, created_at, status in results:
                print(f"📄 {url_hash[:8]} - {url} (Created: {created_at})")
            
            return True
            
        except Exception as e:
            self.print_status(f"Error listing reports: {str(e)}", "error")
            return False
    
    def _generate_report(self, audit_id: str, format_type: str, output_path: str = None):
        """Generate report for specific audit"""
        # This would need to be implemented to regenerate reports from cached data
        self.print_status("Report regeneration feature coming soon", "warning")
        return True
    
    def handle_config_command(self, args):
        """Handle configuration command"""
        if args.config_action == 'show':
            self.print_status("Current configuration...")
            return self._show_config()
        elif args.config_action == 'set':
            self.print_status(f"Setting {args.key} = {args.value}")
            return self._set_config(args.key, args.value)
        elif args.config_action == 'reset':
            self.print_status("Resetting to default configuration...")
            return self._reset_config()
        else:
            self.print_status("Configuration action required", "error")
            self.print_status("Available actions: show, set, reset")
            return False
    
    def _show_config(self):
        """Show current configuration"""
        try:
            config = self.config.load()
            print(f"\n{Colors.HEADER}Current Configuration:{Colors.ENDC}")
            for key, value in config.items():
                print(f"  {key}: {value}")
            return True
        except Exception as e:
            self.print_status(f"Error showing config: {str(e)}", "error")
            return False
    
    def _set_config(self, key: str, value: str):
        """Set configuration value"""
        try:
            # Try to parse value as appropriate type
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
            
            self.config.set(key, value)
            self.print_status(f"Configuration updated: {key} = {value}", "success")
            return True
        except Exception as e:
            self.print_status(f"Error setting config: {str(e)}", "error")
            return False
    
    def _reset_config(self):
        """Reset configuration to defaults"""
        try:
            self.config.reset()
            self.print_status("Configuration reset to defaults", "success")
            return True
        except Exception as e:
            self.print_status(f"Error resetting config: {str(e)}", "error")
            return False


def main():
    """Main CLI entry point."""
    parser = create_parser()
    
    # Special handling for direct URL input (no subcommand)
    if len(sys.argv) == 2 and sys.argv[1].startswith(('http://', 'https://')):
        app = ProbeApp()
        return app.handle_direct_url(sys.argv[1])
    
    args = parser.parse_args()
    
    # Handle cases where no command is provided
    if not args.command:
        parser.print_help()
        return
    
    # Initialize app
    app = ProbeApp()
    
    # Route to appropriate command handlers
    if args.command == 'seo':
        return app.handle_seo_command(args)
    elif args.command == 'server':
        return app.handle_server_command(args)
    elif args.command == 'cache':
        return app.handle_cache_command(args)
    elif args.command == 'report':
        return app.handle_report_command(args)
    elif args.command == 'config':
        return app.handle_config_command(args)


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Operation cancelled by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}❌ Unexpected error: {str(e)}{Colors.ENDC}")
        sys.exit(1)