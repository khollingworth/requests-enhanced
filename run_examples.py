#!/usr/bin/env python3
"""
Wrapper script to run examples in the correct Python environment.
"""

import os
import sys
import importlib.util
import subprocess
from pathlib import Path


def run_example(example_path):
    """Run a single example file and capture its output."""
    print(f"\n{'='*50}")
    print(f"RUNNING EXAMPLE: {os.path.basename(example_path)}")
    print(f"{'='*50}")

    try:
        # Get the module name from the file path
        module_name = os.path.splitext(os.path.basename(example_path))[0]

        # Load the module
        spec = importlib.util.spec_from_file_location(module_name, example_path)
        module = importlib.util.module_from_spec(spec)

        # Add the src directory to sys.path temporarily
        original_path = sys.path.copy()
        sys.path.insert(0, str(Path(__file__).parent / "src"))

        # Execute the module
        spec.loader.exec_module(module)

        # Restore the original path
        sys.path = original_path

        print(f"\n{'='*50}")
        print(f"COMPLETED: {os.path.basename(example_path)}")
        print(f"{'='*50}\n")

    except Exception as e:
        print(f"Error running {example_path}: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Run all example files in the examples directory."""
    # Find all Python files in the examples directory
    examples_dir = Path(__file__).parent / "examples"
    example_files = list(examples_dir.glob("*.py"))

    if not example_files:
        print("No example files found in the examples directory.")
        return

    print(f"Found {len(example_files)} example files.")

    # Run each example
    for example_file in example_files:
        run_example(str(example_file))


if __name__ == "__main__":
    main()
