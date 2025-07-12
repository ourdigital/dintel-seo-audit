#!/usr/bin/env python3
"""
Installation script for probe CLI tool
Creates a system-wide 'probe' command
"""

import os
import sys
import shutil
import stat
from pathlib import Path

def create_probe_executable():
    """Create the probe executable script"""
    
    # Get the current directory (where probe.py is located)
    current_dir = Path(__file__).parent.absolute()
    probe_source = current_dir / 'probe.py'
    
    if not probe_source.exists():
        print("❌ Error: probe.py not found in current directory")
        return False
    
    # Create probe executable content
    probe_content = f'''#!/usr/bin/env python3
"""
probe - Enterprise SEO Audit Toolkit CLI
System-wide executable wrapper
"""

import sys
import os

# Add the probe installation directory to Python path
PROBE_DIR = "{current_dir}"
sys.path.insert(0, PROBE_DIR)

# Change to probe directory for relative imports
os.chdir(PROBE_DIR)

# Import and run probe
from probe import main

if __name__ == '__main__':
    main()
'''
    
    # Determine installation directory
    # Try common locations for user binaries
    possible_dirs = [
        Path.home() / '.local' / 'bin',
        Path.home() / 'bin',
        Path('/usr/local/bin'),
        Path('/usr/bin')
    ]
    
    install_dir = None
    for dir_path in possible_dirs:
        if dir_path.exists():
            try:
                # Test if we can write to this directory
                test_file = dir_path / 'test_probe_install'
                test_file.touch()
                test_file.unlink()
                install_dir = dir_path
                break
            except (PermissionError, OSError):
                continue
    
    if not install_dir:
        # Create ~/.local/bin if nothing else works
        install_dir = Path.home() / '.local' / 'bin'
        install_dir.mkdir(parents=True, exist_ok=True)
    
    # Write the probe executable
    probe_executable = install_dir / 'probe'
    
    try:
        with open(probe_executable, 'w') as f:
            f.write(probe_content)
        
        # Make it executable
        probe_executable.chmod(probe_executable.stat().st_mode | stat.S_IEXEC)
        
        print(f"✅ Successfully installed probe to: {probe_executable}")
        print(f"📁 Installation directory: {install_dir}")
        
        # Check if the directory is in PATH
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        if str(install_dir) not in path_dirs:
            print(f"\n⚠️  Warning: {install_dir} is not in your PATH")
            print("Add this to your shell profile (~/.bashrc, ~/.zshrc, etc.):")
            print(f'export PATH="{install_dir}:$PATH"')
            print("\nOr run probe with full path:")
            print(f"{probe_executable} --help")
        else:
            print(f"\n🎉 Ready to use! Try: probe --help")
        
        return True
        
    except Exception as e:
        print(f"❌ Error installing probe: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    try:
        # Check if we can import required modules
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Test imports
        from cli import SEOAuditCLI
        print("✅ Core modules available")
        
        # Test optional imports
        try:
            from performance_monitor import PerformanceMonitor
            print("✅ Performance monitor available")
        except ImportError:
            print("⚠️  Performance monitor not available (missing psutil - optional)")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("⚠️  Warning: Python 3.8+ recommended")
        else:
            print(f"✅ Python version: {sys.version}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please ensure all required modules are available")
        return False

def main():
    """Main installation function"""
    print("🚀 Installing probe CLI tool...\n")
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Installation failed due to missing dependencies")
        return False
    
    # Create executable
    if not create_probe_executable():
        print("\n❌ Installation failed")
        return False
    
    print("\n🎯 Installation complete!")
    print("\nQuick start:")
    print("  probe --help                    # Show help")
    print("  probe https://example.com       # Quick SEO audit")
    print("  probe seo --interactive         # Guided mode")
    print("  probe server start             # Start web interface")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)