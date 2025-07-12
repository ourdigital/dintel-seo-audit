#!/usr/bin/env python3
"""
Performance Monitoring Script for SEO Audit Tool

Monitors system resources during audit execution to identify performance bottlenecks
and optimization opportunities.
"""

import psutil
import time
import subprocess
import json
import threading
import os
from datetime import datetime
from pathlib import Path

class PerformanceMonitor:
    """Monitor system performance during SEO audits"""
    
    def __init__(self):
        self.metrics = []
        self.monitoring = False
        self.start_time = None
        
    def start_monitoring(self, interval=1):
        """Start performance monitoring"""
        self.monitoring = True
        self.start_time = time.time()
        self.metrics = []
        
        def monitor_loop():
            while self.monitoring:
                try:
                    # Get current system metrics
                    cpu_percent = psutil.cpu_percent(interval=None)
                    memory = psutil.virtual_memory()
                    disk_io = psutil.disk_io_counters()
                    network_io = psutil.net_io_counters()
                    
                    metric = {
                        'timestamp': time.time(),
                        'elapsed': time.time() - self.start_time,
                        'cpu_percent': cpu_percent,
                        'memory_used_mb': memory.used / 1024 / 1024,
                        'memory_percent': memory.percent,
                        'memory_available_mb': memory.available / 1024 / 1024,
                        'disk_read_mb': disk_io.read_bytes / 1024 / 1024 if disk_io else 0,
                        'disk_write_mb': disk_io.write_bytes / 1024 / 1024 if disk_io else 0,
                        'network_sent_mb': network_io.bytes_sent / 1024 / 1024 if network_io else 0,
                        'network_recv_mb': network_io.bytes_recv / 1024 / 1024 if network_io else 0
                    }
                    
                    self.metrics.append(metric)
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    break
                    
        # Start monitoring in background thread
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=2)
            
    def get_summary(self):
        """Get performance summary statistics"""
        if not self.metrics:
            return None
            
        cpu_values = [m['cpu_percent'] for m in self.metrics]
        memory_values = [m['memory_used_mb'] for m in self.metrics]
        
        summary = {
            'duration_seconds': self.metrics[-1]['elapsed'] if self.metrics else 0,
            'total_samples': len(self.metrics),
            'cpu': {
                'avg': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory': {
                'avg_mb': sum(memory_values) / len(memory_values),
                'max_mb': max(memory_values),
                'min_mb': min(memory_values),
                'peak_percent': max(m['memory_percent'] for m in self.metrics)
            },
            'network': {
                'total_sent_mb': self.metrics[-1]['network_sent_mb'] - self.metrics[0]['network_sent_mb'] if len(self.metrics) > 1 else 0,
                'total_recv_mb': self.metrics[-1]['network_recv_mb'] - self.metrics[0]['network_recv_mb'] if len(self.metrics) > 1 else 0
            }
        }
        
        return summary
        
    def save_results(self, output_file, additional_data=None):
        """Save monitoring results to file"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'summary': self.get_summary(),
            'detailed_metrics': self.metrics,
            'additional_data': additional_data or {}
        }
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
        return output_file

def monitor_audit(url, max_pages=50, max_depth=3, output_dir=None):
    """Monitor an SEO audit and generate performance report"""
    if output_dir is None:
        output_dir = Path.home() / '.seo_audit' / 'performance'
        
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    domain = url.replace('https://', '').replace('http://', '').replace('/', '_')
    output_file = output_dir / f"performance_{domain}_{timestamp}.json"
    
    print(f"🔍 Starting monitored audit of {url}")
    print(f"📊 Performance data will be saved to: {output_file}")
    
    # Initialize monitor
    monitor = PerformanceMonitor()
    
    try:
        # Start monitoring
        monitor.start_monitoring(interval=1)
        
        # Run audit
        audit_start = time.time()
        result = subprocess.run([
            'python', 'cli.py', 'audit', 
            '--url', url,
            '--max-pages', str(max_pages),
            '--max-depth', str(max_depth)
        ], capture_output=True, text=True, timeout=1800)  # 30 minute timeout
        
        audit_end = time.time()
        audit_duration = audit_end - audit_start
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Prepare additional data
        additional_data = {
            'audit_config': {
                'url': url,
                'max_pages': max_pages,
                'max_depth': max_depth
            },
            'audit_result': {
                'duration_seconds': audit_duration,
                'return_code': result.returncode,
                'success': result.returncode == 0,
                'stdout_lines': len(result.stdout.split('\n')),
                'stderr_lines': len(result.stderr.split('\n'))
            }
        }
        
        # Save results
        monitor.save_results(output_file, additional_data)
        
        # Print summary
        summary = monitor.get_summary()
        if summary:
            print(f"\n📈 Performance Summary:")
            print(f"   Duration: {summary['duration_seconds']:.1f} seconds")
            print(f"   Avg CPU: {summary['cpu']['avg']:.1f}%")
            print(f"   Peak CPU: {summary['cpu']['max']:.1f}%")
            print(f"   Avg Memory: {summary['memory']['avg_mb']:.1f} MB")
            print(f"   Peak Memory: {summary['memory']['max_mb']:.1f} MB")
            print(f"   Network Sent: {summary['network']['total_sent_mb']:.2f} MB")
            print(f"   Network Received: {summary['network']['total_recv_mb']:.2f} MB")
            
        # Print audit result
        if result.returncode == 0:
            print(f"✅ Audit completed successfully")
        else:
            print(f"❌ Audit failed with code {result.returncode}")
            if result.stderr:
                print(f"Error output: {result.stderr}")
                
        return output_file
        
    except subprocess.TimeoutExpired:
        monitor.stop_monitoring()
        print(f"⏰ Audit timed out after 30 minutes")
        return None
        
    except Exception as e:
        monitor.stop_monitoring()
        print(f"❌ Monitoring failed: {e}")
        return None

def analyze_performance_data(performance_file):
    """Analyze performance data and provide recommendations"""
    with open(performance_file, 'r') as f:
        data = json.load(f)
        
    summary = data['summary']
    audit_config = data['additional_data']['audit_config']
    audit_result = data['additional_data']['audit_result']
    
    print(f"\n📊 Performance Analysis for {audit_config['url']}")
    print(f"=" * 60)
    
    # Efficiency metrics
    pages_per_second = audit_config['max_pages'] / summary['duration_seconds']
    mb_per_page = summary['memory']['avg_mb'] / audit_config['max_pages']
    
    print(f"📈 Efficiency Metrics:")
    print(f"   Pages per second: {pages_per_second:.2f}")
    print(f"   Memory per page: {mb_per_page:.1f} MB")
    print(f"   Total network usage: {summary['network']['total_recv_mb']:.1f} MB")
    
    # Performance assessment
    print(f"\n🎯 Performance Assessment:")
    
    if summary['cpu']['avg'] > 80:
        print(f"   ⚠️  High CPU usage ({summary['cpu']['avg']:.1f}%) - Consider optimization")
    elif summary['cpu']['avg'] > 50:
        print(f"   ⚡ Moderate CPU usage ({summary['cpu']['avg']:.1f}%) - Acceptable")
    else:
        print(f"   ✅ Low CPU usage ({summary['cpu']['avg']:.1f}%) - Efficient")
        
    if summary['memory']['peak_percent'] > 80:
        print(f"   ⚠️  High memory usage ({summary['memory']['peak_percent']:.1f}%) - Risk of OOM")
    elif summary['memory']['peak_percent'] > 60:
        print(f"   ⚡ Moderate memory usage ({summary['memory']['peak_percent']:.1f}%) - Monitor closely")
    else:
        print(f"   ✅ Low memory usage ({summary['memory']['peak_percent']:.1f}%) - Efficient")
        
    if pages_per_second < 0.1:
        print(f"   ⚠️  Slow crawling ({pages_per_second:.3f} pages/sec) - Needs optimization")
    elif pages_per_second < 0.5:
        print(f"   ⚡ Moderate speed ({pages_per_second:.2f} pages/sec) - Acceptable")
    else:
        print(f"   ✅ Fast crawling ({pages_per_second:.2f} pages/sec) - Excellent")
        
    # Recommendations
    print(f"\n💡 Optimization Recommendations:")
    
    if summary['cpu']['avg'] > 60:
        print(f"   • Consider implementing parallel crawling to reduce overall time")
        print(f"   • Add request rate limiting to reduce CPU spikes")
        
    if summary['memory']['peak_percent'] > 70:
        print(f"   • Implement page processing batching to reduce memory usage")
        print(f"   • Add garbage collection between page analyses")
        
    if pages_per_second < 0.2:
        print(f"   • Optimize network requests with connection pooling")
        print(f"   • Implement concurrent page processing")
        print(f"   • Add intelligent page prioritization")
        
    return data

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor SEO audit performance')
    parser.add_argument('--url', required=True, help='Website URL to audit')
    parser.add_argument('--max-pages', type=int, default=50, help='Max pages to crawl')
    parser.add_argument('--max-depth', type=int, default=3, help='Max crawl depth')
    parser.add_argument('--output-dir', help='Output directory for results')
    parser.add_argument('--analyze', help='Analyze existing performance data file')
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze_performance_data(args.analyze)
    else:
        result_file = monitor_audit(args.url, args.max_pages, args.max_depth, args.output_dir)
        if result_file:
            print(f"\n🔍 Analyzing results...")
            analyze_performance_data(result_file)