#!/usr/bin/env python3
import subprocess
import re
from pathlib import Path
from typing import Dict, Optional
import pkg_resources
import requests

def get_installed_version(package_name: str) -> str:
    """Get the installed version of a package using pip."""
    try:
        dist = pkg_resources.get_distribution(package_name)
        return dist.version
    except pkg_resources.DistributionNotFound:
        return "Not installed"

def get_latest_version(package_name: str) -> str:
    """Get the latest version available on PyPI using the JSON API."""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        if response.status_code == 200:
            return response.json()["info"]["version"]
        return "Unknown"
    except Exception:
        return "Unknown"

def parse_requirements(filename: str) -> Dict[str, Optional[str]]:
    """Parse requirements.txt and return a dict of package names and versions."""
    requirements = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = re.split(r'[><=~]=*', line)
                package = parts[0].strip()
                version = parts[1].strip() if len(parts) > 1 else None
                requirements[package] = version
    return requirements

def update_requirements(requirements: Dict[str, Optional[str]], filename: str):
    """Update requirements.txt with new versions."""
    with open(filename, 'w') as f:
        for package, _ in requirements.items():
            latest = get_latest_version(package)
            if latest != "Unknown":
                f.write(f"{package}>={latest}\n")
            else:
                print(f"Warning: Could not determine latest version for {package}")

def main():
    requirements_file = "requirements.txt"
    
    if not Path(requirements_file).exists():
        print(f"Error: {requirements_file} not found")
        return
    
    print("Checking current dependencies...")
    current_requirements = parse_requirements(requirements_file)
    
    print("\nCurrent vs Latest versions:")
    print("-" * 60)
    print(f"{'Package':<30} {'Current':<15} {'Latest':<15}")
    print("-" * 60)
    
    for package in current_requirements:
        current = get_installed_version(package)
        latest = get_latest_version(package)
        print(f"{package:<30} {current:<15} {latest:<15}")
    
    update = input("\nWould you like to update requirements.txt with latest versions? (y/n): ")
    if update.lower() == 'y':
        update_requirements(current_requirements, requirements_file)
        print(f"\nUpdated {requirements_file} with latest versions")
        print("To install updated packages, run: pip install -r requirements.txt")
    else:
        print("\nNo changes made")

if __name__ == "__main__":
    main() 