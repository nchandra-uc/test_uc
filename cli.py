#!/usr/bin/env python3
"""
CLI application with cloud mode support.

When started with --cloud flag, opens the composer picker on launch.
"""

import argparse
import sys


def create_parser():
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Application launcher with cloud mode support.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-c",
        "--cloud",
        action="store_true",
        default=False,
        help="Start in cloud mode (open composer picker on launch) (default: false)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose output (default: false)",
    )
    return parser


def open_composer_picker():
    """Open the composer picker interface for cloud mode."""
    print("Opening composer picker...")
    print("Cloud mode is active. Select a composer to get started:")
    print()
    print("  [1] New Composer")
    print("  [2] Recent Composers")
    print("  [3] Browse Templates")
    print()
    print("Use arrow keys to navigate, Enter to select, or 'q' to quit.")


def start_default_mode(verbose=False):
    """Start the application in default (local) mode."""
    if verbose:
        print("Starting in default (local) mode...")
    print("Application started. Use -c or --cloud to start in cloud mode.")


def main(args=None):
    """Main entry point for the CLI application."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if parsed_args.verbose:
        print(f"Cloud mode: {parsed_args.cloud}")

    if parsed_args.cloud:
        open_composer_picker()
    else:
        start_default_mode(verbose=parsed_args.verbose)

    return 0


if __name__ == "__main__":
    sys.exit(main())
