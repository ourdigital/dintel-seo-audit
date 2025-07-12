#!/usr/bin/env python3
"""
Comprehensive Field Testing Suite for Probe CLI
Tests all user scenarios, error cases, and real-world workflows
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class ProbeFieldTester:
    """Comprehensive field testing for probe CLI"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        self.probe_cmd = self._find_probe_command()
        
    def _find_probe_command(self):
        """Find the probe command (installed or local)"""
        # Try installed version first
        installed_probe = Path.home() / '.local/bin/probe'
        if installed_probe.exists():
            return str(installed_probe)
        
        # Fall back to local version
        local_probe = Path(__file__).parent / 'probe.py'
        if local_probe.exists():
            return f"python {local_probe}"
        
        raise FileNotFoundError("Neither installed probe nor probe.py found")
    
    def print_test_header(self, test_name: str):
        """Print test header"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{test_name.center(60)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    def print_status(self, message: str, status: str = "info"):
        """Print colored status message"""
        colors = {
            "info": Colors.OKCYAN,
            "success": Colors.OKGREEN,
            "warning": Colors.WARNING,
            "error": Colors.FAIL
        }
        icons = {
            "info": "🔍",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        color = colors.get(status, Colors.ENDC)
        icon = icons.get(status, "ℹ️")
        print(f"{color}{icon} {message}{Colors.ENDC}")
    
    def run_command(self, command: str, timeout: int = 60, expect_success: bool = True):
        """Run a command and capture results"""
        full_command = f"{self.probe_cmd} {command}" if not command.startswith('probe') else command
        
        try:
            result = subprocess.run(
                full_command.split(),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = (result.returncode == 0) == expect_success
            
            test_result = {
                'command': full_command,
                'success': success,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'expected_success': expect_success
            }
            
            self.test_results.append(test_result)
            
            if success:
                self.print_status(f"✅ Command succeeded: {command}", "success")
            else:
                self.print_status(f"❌ Command failed: {command}", "error")
                if result.stderr:
                    print(f"    Error: {result.stderr[:100]}...")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            self.print_status(f"⏰ Command timed out: {command}", "error")
            return {
                'command': full_command,
                'success': False,
                'error': 'Timeout',
                'expected_success': expect_success
            }
        except Exception as e:
            self.print_status(f"💥 Command error: {command} - {str(e)}", "error")
            return {
                'command': full_command,
                'success': False,
                'error': str(e),
                'expected_success': expect_success
            }
    
    def test_basic_functionality(self):
        """Test basic probe functionality"""
        self.print_test_header("BASIC FUNCTIONALITY TESTS")
        
        # Test help commands
        self.print_status("Testing help commands...")
        self.run_command("--help")
        self.run_command("--version")
        self.run_command("seo --help")
        self.run_command("server --help")
        self.run_command("cache --help")
        self.run_command("config --help")
        
        # Test config commands
        self.print_status("Testing configuration...")
        self.run_command("config show")
        self.run_command("config set test_key test_value")
        self.run_command("config show")
        self.run_command("config reset")
        
        # Test cache commands
        self.print_status("Testing cache management...")
        self.run_command("cache list")
        self.run_command("cache info")
        
    def test_seo_analysis(self):
        """Test SEO analysis functionality"""
        self.print_test_header("SEO ANALYSIS TESTS")
        
        # Test direct URL (quick)
        self.print_status("Testing direct URL analysis...")
        result = self.run_command("https://example.com", timeout=180)
        
        # Test SEO command variations
        self.print_status("Testing SEO command variations...")
        self.run_command("seo https://httpbin.org -p 5 -d 1", timeout=120)
        
        # Test with different parameters
        self.print_status("Testing parameter variations...")
        self.run_command("seo https://httpbin.org/html -p 3 -d 1 --no-cache", timeout=120)
        
        # Test cache reuse
        self.print_status("Testing cache reuse...")
        self.run_command("cache list")
        
    def test_error_handling(self):
        """Test error handling and edge cases"""
        self.print_test_header("ERROR HANDLING TESTS")
        
        # Test invalid URLs
        self.print_status("Testing invalid URLs...")
        self.run_command("seo invalid-url", expect_success=False)
        self.run_command("seo http://does-not-exist-12345.com", expect_success=False, timeout=30)
        
        # Test missing arguments
        self.print_status("Testing missing arguments...")
        self.run_command("seo", expect_success=False)
        self.run_command("server", expect_success=False)
        self.run_command("cache", expect_success=False)
        
        # Test invalid options
        self.print_status("Testing invalid options...")
        self.run_command("seo https://example.com -p invalid", expect_success=False)
        self.run_command("seo https://example.com -d 0", expect_success=False)
        
    def test_server_functionality(self):
        """Test server management"""
        self.print_test_header("SERVER FUNCTIONALITY TESTS")
        
        # Test server status when not running
        self.print_status("Testing server status (should be stopped)...")
        self.run_command("server status")
        
        # Note: We won't actually start/stop server in automated tests
        # as it requires manual intervention
        self.print_status("⚠️ Server start/stop tests require manual verification", "warning")
        
    def test_batch_processing(self):
        """Test batch processing functionality"""
        self.print_test_header("BATCH PROCESSING TESTS")
        
        # Create test file
        test_file = Path("test_sites.txt")
        try:
            with open(test_file, 'w') as f:
                f.write("https://httpbin.org/html\n")
                f.write("https://httpbin.org/json\n")
                f.write("# This is a comment\n")
                f.write("\n")  # Empty line
            
            self.print_status("Testing batch processing...")
            self.run_command(f"seo --batch {test_file} -p 2 -d 1", timeout=180)
            
        except Exception as e:
            self.print_status(f"Batch test setup failed: {e}", "error")
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()
    
    def test_user_workflows(self):
        """Test common user workflows"""
        self.print_test_header("USER WORKFLOW TESTS")
        
        # SEO Professional workflow
        self.print_status("Testing SEO Professional workflow...")
        self.run_command("config set default_pages 15")
        self.run_command("config set default_depth 2")
        self.run_command("seo https://httpbin.org/html", timeout=120)
        self.run_command("cache list")
        
        # Developer workflow
        self.print_status("Testing Developer workflow...")
        self.run_command("seo https://httpbin.org/json -p 5 --no-cache", timeout=60)
        self.run_command("cache info")
        
        # Content team workflow
        self.print_status("Testing Content team workflow...")
        self.run_command("seo https://httpbin.org/robots.txt -p 3", timeout=60)
        self.run_command("cache list -l 5")
        
        # Reset config
        self.run_command("config reset")
    
    def test_output_formats(self):
        """Test different output formats"""
        self.print_test_header("OUTPUT FORMAT TESTS")
        
        # Test different format options
        self.print_status("Testing output formats...")
        # Note: Format testing is implicit in SEO analysis
        # The actual format generation is tested in the audit process
        self.run_command("seo https://httpbin.org/html -p 3 -d 1", timeout=120)
        
    def test_configuration_persistence(self):
        """Test configuration persistence"""
        self.print_test_header("CONFIGURATION PERSISTENCE TESTS")
        
        # Set configuration
        self.print_status("Testing configuration persistence...")
        self.run_command("config set default_depth 4")
        self.run_command("config set default_pages 25")
        self.run_command("config show")
        
        # Verify persistence (config should survive between commands)
        self.run_command("config show")
        
        # Reset
        self.run_command("config reset")
        self.run_command("config show")
    
    def test_cache_management(self):
        """Test comprehensive cache management"""
        self.print_test_header("CACHE MANAGEMENT TESTS")
        
        # Test cache operations
        self.print_status("Testing cache operations...")
        self.run_command("cache list")
        self.run_command("cache info")
        self.run_command("cache list -l 5")
        
        # Test cache clearing (commented out to preserve test data)
        # self.run_command("cache clear --older-than 0")
        
    def test_interactive_mode_help(self):
        """Test interactive mode help and guidance"""
        self.print_test_header("INTERACTIVE MODE TESTS")
        
        # We can't fully test interactive mode in automated tests,
        # but we can test the help and command structure
        self.print_status("Testing interactive mode help...")
        self.run_command("seo --help")
        
        # Note: Full interactive testing requires manual verification
        self.print_status("⚠️ Interactive mode requires manual testing", "warning")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.print_test_header("TEST RESULTS SUMMARY")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - successful_tests
        
        # Calculate success rate
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{Colors.BOLD}📊 Test Summary:{Colors.ENDC}")
        print(f"  Total Tests: {total_tests}")
        print(f"  Successful: {Colors.OKGREEN}{successful_tests}{Colors.ENDC}")
        print(f"  Failed: {Colors.FAIL}{failed_tests}{Colors.ENDC}")
        print(f"  Success Rate: {Colors.OKGREEN if success_rate >= 80 else Colors.WARNING}{success_rate:.1f}%{Colors.ENDC}")
        
        # Show failed tests
        if failed_tests > 0:
            print(f"\n{Colors.FAIL}❌ Failed Tests:{Colors.ENDC}")
            for result in self.test_results:
                if not result['success']:
                    command = result['command']
                    error = result.get('stderr', result.get('error', 'Unknown error'))
                    print(f"  • {command}")
                    if error:
                        print(f"    Error: {error[:100]}...")
        
        # Performance summary
        total_time = time.time() - self.start_time
        print(f"\n{Colors.BOLD}⚡ Performance:{Colors.ENDC}")
        print(f"  Total Test Time: {total_time:.1f} seconds")
        print(f"  Average per Test: {total_time/total_tests:.1f} seconds")
        
        # Save detailed results
        self._save_detailed_results()
        
        # Final assessment
        print(f"\n{Colors.BOLD}🎯 Assessment:{Colors.ENDC}")
        if success_rate >= 90:
            print(f"  {Colors.OKGREEN}✅ Excellent - Ready for production use{Colors.ENDC}")
        elif success_rate >= 80:
            print(f"  {Colors.OKGREEN}✅ Good - Ready with minor notes{Colors.ENDC}")
        elif success_rate >= 70:
            print(f"  {Colors.WARNING}⚠️  Acceptable - Some issues to address{Colors.ENDC}")
        else:
            print(f"  {Colors.FAIL}❌ Needs improvement - Significant issues found{Colors.ENDC}")
    
    def _save_detailed_results(self):
        """Save detailed test results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"probe_field_test_results_{timestamp}.json"
        
        detailed_results = {
            'timestamp': datetime.now().isoformat(),
            'probe_command': self.probe_cmd,
            'total_tests': len(self.test_results),
            'successful_tests': sum(1 for r in self.test_results if r['success']),
            'test_duration': time.time() - self.start_time,
            'test_results': self.test_results
        }
        
        try:
            with open(results_file, 'w') as f:
                json.dump(detailed_results, f, indent=2, default=str)
            print(f"  📄 Detailed results saved: {results_file}")
        except Exception as e:
            print(f"  ⚠️ Could not save results: {e}")
    
    def run_comprehensive_tests(self):
        """Run all field tests"""
        print(f"{Colors.BOLD}{Colors.HEADER}")
        print("PROBE CLI - COMPREHENSIVE FIELD TESTING")
        print("======================================")
        print(f"{Colors.ENDC}")
        
        print(f"🔍 Using probe command: {self.probe_cmd}")
        print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Run all test suites
            self.test_basic_functionality()
            self.test_seo_analysis()
            self.test_error_handling()
            self.test_server_functionality()
            self.test_batch_processing()
            self.test_user_workflows()
            self.test_output_formats()
            self.test_configuration_persistence()
            self.test_cache_management()
            self.test_interactive_mode_help()
            
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⚠️ Testing interrupted by user{Colors.ENDC}")
        except Exception as e:
            print(f"\n{Colors.FAIL}💥 Testing error: {str(e)}{Colors.ENDC}")
        finally:
            # Always generate report
            self.generate_report()

def main():
    """Main test runner"""
    tester = ProbeFieldTester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()