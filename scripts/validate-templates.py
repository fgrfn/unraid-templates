#!/usr/bin/env python3
"""
Validates Unraid XML templates to ensure they meet quality standards.
This script checks:
- All templates have icon URLs filled in
- Icon URLs use HTTPS
- Required fields are present
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import sys

def validate_template(xml_path):
    """
    Validate a single XML template for compliance with template standards.
    
    Args:
        xml_path: Path to the XML template file
        
    Returns:
        tuple: (errors, warnings) where:
            - errors: List of critical validation failures that must be fixed
            - warnings: List of non-critical issues that should be reviewed
            
    Validation checks:
        - Icon URL is present and non-empty (error if missing)
        - Icon URL uses HTTPS protocol (warning if not)
        - Name field is present and non-empty (error if missing)
        - Repository field is present and non-empty (error if missing)
    """
    errors = []
    warnings = []
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Check for Icon field
        icon = root.findtext('Icon', '')
        if not icon.strip():
            errors.append("Missing or empty Icon URL")
        elif not icon.startswith('https://'):
            warnings.append(f"Icon URL should use HTTPS: {icon}")
        
        # Check for other important fields
        name = root.findtext('Name', '')
        if not name.strip():
            errors.append("Missing or empty Name field")
            
        repository = root.findtext('Repository', '')
        if not repository.strip():
            errors.append("Missing or empty Repository field")
        
        return errors, warnings
        
    except Exception as e:
        return [f"XML parsing error: {e}"], []

def main():
    """Main validation function"""
    repo_root = Path(__file__).parent.parent
    templates_dir = repo_root / 'templates'
    
    print("🔍 Validating Unraid templates...\n")
    
    has_errors = False
    templates_checked = 0
    
    # Find all XML templates (excluding blank-template.xml)
    for xml_file in templates_dir.rglob('*.xml'):
        # Skip the blank template as it's intentionally a placeholder
        if 'blank-template' in xml_file.name:
            continue
        
        templates_checked += 1
        relative_path = xml_file.relative_to(repo_root)
        
        errors, warnings = validate_template(xml_file)
        
        if errors or warnings:
            print(f"📄 {relative_path}")
            
            if errors:
                has_errors = True
                for error in errors:
                    print(f"   ❌ ERROR: {error}")
                    
            if warnings:
                for warning in warnings:
                    print(f"   ⚠️  WARNING: {warning}")
            
            print()
    
    print(f"✅ Validated {templates_checked} template(s)")
    
    if has_errors:
        print("\n❌ Validation failed! Please fix the errors above.")
        sys.exit(1)
    else:
        print("\n✅ All templates are valid!")
        sys.exit(0)

if __name__ == '__main__':
    main()
