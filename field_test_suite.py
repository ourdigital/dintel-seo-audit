#!/usr/bin/env python3
"""
Comprehensive Field Testing Suite for SEO Audit Tool

Automated testing with various website types, edge cases, and performance monitoring.
"""

import subprocess
import json
import time
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import threading
import queue

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

class FieldTestSuite:
    """Comprehensive field testing suite"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.test_queue = queue.Queue()
        
    def run_test_case(self, test_case):
        """Run a single test case"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}Testing: {test_case['name']}{Colors.ENDC}")
        print(f"{Colors.HEADER}URL: {test_case['url']}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        start_time = time.time()
        
        try:
            # Run the audit
            cmd = [
                'python', 'cli.py', 'audit',
                '--url', test_case['url'],
                '--max-pages', str(test_case.get('max_pages', 10)),
                '--max-depth', str(test_case.get('max_depth', 2))
            ]
            
            print(f"{Colors.OKCYAN}Command: {' '.join(cmd)}{Colors.ENDC}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=test_case.get('timeout', 600)  # 10 minute default timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Analyze result
            success = result.returncode == 0
            
            test_result = {
                'test_case': test_case,
                'start_time': start_time,
                'duration': duration,
                'success': success,
                'return_code': result.returncode,
                'stdout_lines': len(result.stdout.split('\n')),
                'stderr_lines': len(result.stderr.split('\n')),
                'error_output': result.stderr if result.stderr else None,
                'performance': self._analyze_performance(result.stdout)
            }
            
            # Print results
            if success:
                print(f"{Colors.OKGREEN}✅ SUCCESS{Colors.ENDC} - Completed in {duration:.1f}s")
                self._print_performance_summary(test_result['performance'])
            else:
                print(f"{Colors.FAIL}❌ FAILED{Colors.ENDC} - Code: {result.returncode}")
                if result.stderr:
                    print(f"{Colors.WARNING}Error: {result.stderr[:200]}...{Colors.ENDC}")
                    
            return test_result
            
        except subprocess.TimeoutExpired:
            print(f"{Colors.FAIL}⏰ TIMEOUT{Colors.ENDC} - Exceeded {test_case.get('timeout', 600)}s")
            return {
                'test_case': test_case,
                'start_time': start_time,
                'duration': test_case.get('timeout', 600),
                'success': False,
                'return_code': -1,
                'error_output': 'Timeout expired',
                'performance': None
            }
            
        except Exception as e:
            print(f"{Colors.FAIL}💥 ERROR{Colors.ENDC} - {str(e)}")
            return {
                'test_case': test_case,
                'start_time': start_time,
                'duration': time.time() - start_time,
                'success': False,
                'return_code': -2,
                'error_output': str(e),
                'performance': None
            }
            
    def _analyze_performance(self, stdout):
        """Extract performance metrics from audit output"""
        lines = stdout.split('\n')
        
        # Look for specific patterns
        performance = {
            'pages_found': None,
            'steps_completed': 0,
            'generated_files': []
        }
        
        for line in lines:
            # Pages found
            if '✅ Found' in line and 'pages' in line:
                try:
                    performance['pages_found'] = int(line.split('Found')[1].split('pages')[0].strip())
                except:
                    pass
                    
            # Steps completed
            if '✅' in line and 'completed' in line:
                performance['steps_completed'] += 1
                
            # Generated files
            if 'presentation:' in line or 'report:' in line:
                performance['generated_files'].append(line.strip())
                
        return performance
        
    def _print_performance_summary(self, performance):
        """Print performance summary"""
        if not performance:
            return
            
        if performance['pages_found']:
            print(f"   📄 Pages: {performance['pages_found']}")
        print(f"   ✅ Steps: {performance['steps_completed']}/8")
        print(f"   📁 Files: {len(performance['generated_files'])}")
        
    def run_comprehensive_tests(self):
        """Run the full test suite"""
        self.start_time = time.time()
        
        print(f"{Colors.BOLD}{Colors.HEADER}")
        print("SEO AUDIT TOOL - COMPREHENSIVE FIELD TESTING")
        print("============================================")
        print(f"{Colors.ENDC}")
        
        # Define test cases
        test_cases = [
            # Basic functionality tests
            {
                'name': 'Small Business Website',
                'url': 'https://example.com',
                'max_pages': 5,
                'max_depth': 2,
                'category': 'basic',
                'timeout': 300
            },
            {
                'name': 'Blog Site (Real Test)',
                'url': 'https://ourdigital.org',
                'max_pages': 10,
                'max_depth': 3,
                'category': 'blog',
                'timeout': 600
            },
            {
                'name': 'GitHub (Developer Platform)',
                'url': 'https://github.com',
                'max_pages': 15,
                'max_depth': 2,
                'category': 'tech',
                'timeout': 600
            },
            
            # International sites
            {
                'name': 'Korean Portal Site',
                'url': 'https://naver.com',
                'max_pages': 10,
                'max_depth': 2,
                'category': 'international',
                'timeout': 600
            },
            
            # E-commerce sites
            {
                'name': 'E-commerce Platform',
                'url': 'https://shopify.com',
                'max_pages': 20,
                'max_depth': 2,
                'category': 'ecommerce',
                'timeout': 800
            },
            
            # Documentation sites
            {
                'name': 'Documentation Site',
                'url': 'https://docs.python.org',
                'max_pages': 15,
                'max_depth': 3,
                'category': 'docs',
                'timeout': 600
            },
            
            # News/Content sites
            {
                'name': 'News Website',
                'url': 'https://bbc.com',
                'max_pages': 20,
                'max_depth': 2,
                'category': 'news',
                'timeout': 800
            },
            
            # Stress tests
            {
                'name': 'Large Site Stress Test',
                'url': 'https://wikipedia.org',
                'max_pages': 50,
                'max_depth': 3,
                'category': 'stress',
                'timeout': 1200
            }
        ]
        
        # Run tests
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{Colors.OKBLUE}[{i}/{len(test_cases)}] Starting test...{Colors.ENDC}")
            
            result = self.run_test_case(test_case)
            self.results.append(result)
            
            # Brief pause between tests
            if i < len(test_cases):
                print(f"{Colors.OKCYAN}Waiting 5 seconds before next test...{Colors.ENDC}")
                time.sleep(5)
                
        # Generate final report
        self.generate_final_report()
        
    def run_quick_tests(self):
        """Run a quick subset of tests for rapid validation"""
        self.start_time = time.time()
        
        print(f"{Colors.BOLD}{Colors.HEADER}")
        print("SEO AUDIT TOOL - QUICK FIELD TESTING")
        print("===================================")
        print(f"{Colors.ENDC}")
        
        quick_tests = [
            {
                'name': 'Basic Functionality',
                'url': 'https://example.com',
                'max_pages': 3,
                'max_depth': 1,
                'timeout': 180
            },
            {
                'name': 'Real Website Test',
                'url': 'https://ourdigital.org',
                'max_pages': 5,
                'max_depth': 2,
                'timeout': 300
            },
            {
                'name': 'Korean Content Test',
                'url': 'https://naver.com',
                'max_pages': 5,
                'max_depth': 1,
                'timeout': 300
            }
        ]
        
        for i, test_case in enumerate(quick_tests, 1):
            print(f"\n{Colors.OKBLUE}[{i}/{len(quick_tests)}] Quick test...{Colors.ENDC}")
            result = self.run_test_case(test_case)
            self.results.append(result)
            
        self.generate_final_report()
        
    def run_performance_tests(self):
        """Run performance-focused tests"""
        self.start_time = time.time()
        
        print(f"{Colors.BOLD}{Colors.HEADER}")
        print("SEO AUDIT TOOL - PERFORMANCE TESTING")
        print("===================================")
        print(f"{Colors.ENDC}")
        
        perf_tests = [
            {
                'name': 'Small Site Performance',
                'url': 'https://example.com',
                'max_pages': 10,
                'max_depth': 2,
                'timeout': 300
            },
            {
                'name': 'Medium Site Performance',
                'url': 'https://ourdigital.org',
                'max_pages': 25,
                'max_depth': 3,
                'timeout': 600
            },
            {
                'name': 'Large Site Performance',
                'url': 'https://github.com',
                'max_pages': 50,
                'max_depth': 3,
                'timeout': 1200
            }
        ]
        
        for test_case in perf_tests:
            # Run with performance monitoring
            print(f"\n{Colors.OKBLUE}Running performance test: {test_case['name']}{Colors.ENDC}")
            
            # Start performance monitor
            monitor_cmd = [
                'python', 'performance_monitor.py',
                '--url', test_case['url'],
                '--max-pages', str(test_case['max_pages']),
                '--max-depth', str(test_case['max_depth'])
            ]
            
            start_time = time.time()
            try:
                result = subprocess.run(monitor_cmd, capture_output=True, text=True, 
                                     timeout=test_case['timeout'])
                duration = time.time() - start_time
                
                test_result = {
                    'test_case': test_case,
                    'duration': duration,
                    'success': result.returncode == 0,
                    'performance_monitoring': True,
                    'output': result.stdout
                }
                
                self.results.append(test_result)
                
                if result.returncode == 0:
                    print(f"{Colors.OKGREEN}✅ Performance test completed in {duration:.1f}s{Colors.ENDC}")
                else:
                    print(f"{Colors.FAIL}❌ Performance test failed{Colors.ENDC}")
                    
            except subprocess.TimeoutExpired:
                print(f"{Colors.FAIL}⏰ Performance test timed out{Colors.ENDC}")
                
        self.generate_final_report()
        
    def generate_final_report(self):
        """Generate comprehensive test report"""
        end_time = time.time()
        total_duration = end_time - self.start_time
        
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("FINAL TEST REPORT")
        print("================")
        print(f"{Colors.ENDC}")
        
        # Summary statistics
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {Colors.OKGREEN}{successful_tests}{Colors.ENDC}")
        print(f"   Failed: {Colors.FAIL}{failed_tests}{Colors.ENDC}")
        print(f"   Success Rate: {(successful_tests/total_tests*100):.1f}%")
        print(f"   Total Duration: {total_duration:.1f}s")
        
        if successful_tests > 0:
            avg_duration = sum(r['duration'] for r in self.results if r['success']) / successful_tests
            print(f"   Avg Test Duration: {avg_duration:.1f}s")
            
        # Category breakdown
        categories = {}
        for result in self.results:
            category = result['test_case'].get('category', 'unknown')
            if category not in categories:
                categories[category] = {'total': 0, 'success': 0}
            categories[category]['total'] += 1
            if result['success']:
                categories[category]['success'] += 1
                
        if categories:
            print(f"\n📈 Results by Category:")
            for category, stats in categories.items():
                success_rate = (stats['success'] / stats['total']) * 100
                color = Colors.OKGREEN if success_rate >= 80 else Colors.WARNING if success_rate >= 50 else Colors.FAIL
                print(f"   {category}: {color}{stats['success']}/{stats['total']} ({success_rate:.1f}%){Colors.ENDC}")
                
        # Failed tests details
        if failed_tests > 0:
            print(f"\n{Colors.FAIL}❌ Failed Tests:{Colors.ENDC}")
            for result in self.results:
                if not result['success']:
                    name = result['test_case']['name']
                    error = result.get('error_output', 'Unknown error')[:100]
                    print(f"   • {name}: {error}")
                    
        # Performance insights
        if successful_tests > 0:
            durations = [r['duration'] for r in self.results if r['success']]
            min_duration = min(durations)
            max_duration = max(durations)
            
            print(f"\n⚡ Performance Insights:")
            print(f"   Fastest Test: {min_duration:.1f}s")
            print(f"   Slowest Test: {max_duration:.1f}s")
            
            # Find performance outliers
            avg_duration = sum(durations) / len(durations)
            slow_tests = [r for r in self.results if r['success'] and r['duration'] > avg_duration * 1.5]
            
            if slow_tests:
                print(f"   Slow Tests ({len(slow_tests)}):")
                for test in slow_tests:
                    print(f"     • {test['test_case']['name']}: {test['duration']:.1f}s")
                    
        # Save detailed results
        self.save_detailed_results()
        
        # Final recommendation
        print(f"\n🎯 Recommendation:")
        if (successful_tests / total_tests) >= 0.8:
            print(f"   {Colors.OKGREEN}✅ Tool is ready for production use{Colors.ENDC}")
        elif (successful_tests / total_tests) >= 0.6:
            print(f"   {Colors.WARNING}⚠️  Tool needs minor fixes before production{Colors.ENDC}")
        else:
            print(f"   {Colors.FAIL}❌ Tool requires significant improvements{Colors.ENDC}")
            
    def save_detailed_results(self):
        """Save detailed test results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"field_test_results_{timestamp}.json"
        
        detailed_results = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': len(self.results),
                'successful_tests': sum(1 for r in self.results if r['success']),
                'total_duration': time.time() - self.start_time if self.start_time else 0
            },
            'test_results': self.results
        }
        
        with open(results_file, 'w') as f:
            json.dump(detailed_results, f, indent=2, default=str)
            
        print(f"\n💾 Detailed results saved to: {results_file}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SEO Audit Field Testing Suite')
    parser.add_argument('--mode', choices=['quick', 'comprehensive', 'performance'], 
                       default='quick', help='Testing mode')
    parser.add_argument('--url', help='Test specific URL')
    parser.add_argument('--max-pages', type=int, default=10, help='Max pages for single URL test')
    
    args = parser.parse_args()
    
    suite = FieldTestSuite()
    
    if args.url:
        # Single URL test
        test_case = {
            'name': f'Custom Test - {args.url}',
            'url': args.url,
            'max_pages': args.max_pages,
            'max_depth': 3,
            'timeout': 600
        }
        
        result = suite.run_test_case(test_case)
        suite.results = [result]
        suite.generate_final_report()
        
    elif args.mode == 'quick':
        suite.run_quick_tests()
    elif args.mode == 'comprehensive':
        suite.run_comprehensive_tests()
    elif args.mode == 'performance':
        suite.run_performance_tests()

if __name__ == "__main__":
    main()