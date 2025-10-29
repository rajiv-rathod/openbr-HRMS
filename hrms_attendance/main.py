#!/usr/bin/env python3
"""
Main entry point for HRMS Biometric Attendance Module
"""

import sys
import os
import argparse

# Add parent directory to path to allow proper imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from hrms_attendance.config.settings import AttendanceConfig
from hrms_attendance.core.attendance import AttendanceManager
from hrms_attendance.api.flask_api import run_api_server


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='HRMS Biometric Attendance System - ZKTeco Compatible',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run the API server
  python main.py --mode api --config config.json
  
  # Display current configuration
  python main.py --mode config --config config.json
  
  # Run basic example
  python main.py --mode example
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['api', 'config', 'example'],
        default='example',
        help='Operating mode: api (run server), config (show config), example (run example)'
    )
    
    parser.add_argument(
        '--config',
        default=None,
        help='Path to configuration JSON file'
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='API server host (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='API server port (default: 8080)'
    )
    
    args = parser.parse_args()
    
    # Load or create configuration
    if args.config and os.path.exists(args.config):
        config = AttendanceConfig.from_file(args.config)
        print(f"✓ Loaded configuration from: {args.config}")
    else:
        config = AttendanceConfig()
        if args.config:
            print(f"✓ Created new configuration")
    
    # Execute based on mode
    if args.mode == 'config':
        print(config.display_config())
        
        if args.config and not os.path.exists(args.config):
            config.save_to_file(args.config)
            print(f"\n✓ Configuration saved to: {args.config}")
    
    elif args.mode == 'api':
        print("\nStarting API server...")
        run_api_server(config, host=args.host, port=args.port)
    
    elif args.mode == 'example':
        print("\nRunning basic usage example...")
        # Import and run example
        from hrms_attendance.examples import basic_usage
        basic_usage.main()


if __name__ == '__main__':
    main()
