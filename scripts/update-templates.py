#!/usr/bin/env python3
"""
Automatically checks upstream project repositories for changes
and updates Unraid templates accordingly.

This script:
1. Fetches docker-compose.yml from upstream projects
2. Extracts environment variables, ports, and volumes
3. Compares with current template XML files
4. Updates templates if new variables/config found
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import requests
import yaml
import sys
import re
from typing import Dict, List, Optional

# Template configurations with upstream project information
TEMPLATE_CONFIGS = {
    "Bambuddy": {
        "xml_path": "templates/Bambuddy/my-Bambuddy.xml",
        "upstream_repo": "maziggy/bambuddy",
        "docker_compose_url": "https://raw.githubusercontent.com/maziggy/bambuddy/main/docker-compose.yml",
        "docker_image": "ghcr.io/maziggy/bambuddy"
    },
    "Scan2Target": {
        "xml_path": "templates/Scan2Target/my-Scan2Target.xml",
        "upstream_repo": "fgrfn/Scan2Target",
        "docker_compose_url": "https://raw.githubusercontent.com/fgrfn/Scan2Target/main/docker-compose.yml",
        "docker_image": "ghcr.io/fgrfn/scan2target"
    },
    "Netzbremse": {
        "xml_path": "templates/Netzbremse/my-Netzbremse.xml",
        "upstream_repo": "AKVorrat/netzbremse-measurement",
        "docker_compose_url": "https://raw.githubusercontent.com/AKVorrat/netzbremse-measurement/main/docker-compose.yml",
        "docker_image": "ghcr.io/akvorrat/netzbremse-measurement"
    },
    "RedditWSBCrawler": {
        "xml_path": "templates/RedditWSBCrawler/my-RedditWSBCrawler.xml",
        "upstream_repo": "fgrfn/reddit-wsb-crawler",
        "docker_compose_url": "https://raw.githubusercontent.com/fgrfn/reddit-wsb-crawler/main/docker-compose.yml",
        "docker_image": "ghcr.io/fgrfn/reddit-wsb-crawler"
    }
}

def fetch_docker_compose(url: str) -> Optional[Dict]:
    """
    Fetch docker-compose.yml from upstream repository.
    
    Args:
        url: URL to docker-compose.yml
        
    Returns:
        Parsed docker-compose dict or None if not found
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return yaml.safe_load(response.text)
        else:
            print(f"  ⚠️  Could not fetch docker-compose.yml: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"  ⚠️  Error fetching docker-compose.yml: {e}")
        return None

def extract_default_value(value: str) -> str:
    """
    Extract default value from shell variable syntax.
    
    Examples:
        ${PORT:-8000} -> 8000
        ${VAR} -> ""
        simple_value -> simple_value
    
    Args:
        value: Shell variable expression or simple value
        
    Returns:
        Extracted default value
    """
    if not value:
        return ""
    
    # Match ${VAR:-default} or ${VAR-default}
    match = re.match(r'\$\{[^:}]+(:-?|-)([^}]*)\}', str(value))
    if match:
        return match.group(2)
    
    # Match ${VAR} without default
    if re.match(r'\$\{[^}]+\}', str(value)):
        return ""
    
    # Return as-is if not a variable
    return str(value)

def extract_service_config(compose_data: Dict) -> Optional[Dict]:
    """
    Extract first service configuration from docker-compose.
    
    Args:
        compose_data: Parsed docker-compose.yml
        
    Returns:
        Service configuration dict with env vars, ports, volumes
    """
    if not compose_data or 'services' not in compose_data:
        return None
    
    # Get first service (usually there's only one)
    service_name = list(compose_data['services'].keys())[0]
    service = compose_data['services'][service_name]
    
    config = {
        'environment': {},
        'ports': [],
        'volumes': []
    }
    
    # Extract environment variables
    if 'environment' in service:
        env = service['environment']
        if isinstance(env, dict):
            # Process values to extract defaults from shell syntax
            for key, value in env.items():
                config['environment'][key] = extract_default_value(value)
        elif isinstance(env, list):
            # Parse KEY=VALUE format
            for item in env:
                if '=' in item:
                    key, value = item.split('=', 1)
                    config['environment'][key] = extract_default_value(value)
    
    # Extract ports
    if 'ports' in service:
        config['ports'] = service['ports']
    
    # Extract volumes
    if 'volumes' in service:
        config['volumes'] = service['volumes']
    
    return config

def parse_template_xml(xml_path: Path) -> ET.ElementTree:
    """
    Parse Unraid template XML file.
    
    Args:
        xml_path: Path to XML template
        
    Returns:
        Parsed ElementTree
    """
    return ET.parse(xml_path)

def get_template_env_vars(tree: ET.ElementTree) -> Dict[str, str]:
    """
    Extract environment variables from template XML.
    
    Args:
        tree: Parsed template XML tree
        
    Returns:
        Dict of env var names to their default values
    """
    root = tree.getroot()
    env_vars = {}
    
    for config in root.findall('Config'):
        mode = config.get('Mode', '')
        if mode == 'env':
            target = config.get('Target', '')
            default = config.get('Default', '')
            env_vars[target] = default
    
    return env_vars

def add_env_var_to_template(root: ET.Element, var_name: str, var_value: str = "", description: str = "", display: str = "advanced", required: str = "false", mask: str = "false"):
    """
    Add new environment variable to template XML.
    
    Args:
        root: XML root element
        var_name: Environment variable name
        var_value: Default value
        description: Description text
        display: Display mode (always/advanced)
        required: Required flag
        mask: Mask flag (for sensitive data)
    """
    config = ET.SubElement(root, 'Config')
    config.set('Name', var_name)
    config.set('Target', var_name)
    config.set('Default', var_value)
    config.set('Mode', 'env')
    config.set('Description', description or f"Environment variable: {var_name}")
    config.set('Type', 'Variable')
    config.set('Display', display)
    config.set('Required', required)
    config.set('Mask', mask)
    config.text = var_value

def update_template(template_name: str, config: Dict) -> bool:
    """
    Update a template with new configuration from upstream.
    
    Args:
        template_name: Name of the template
        config: Template configuration
        
    Returns:
        True if template was updated, False otherwise
    """
    print(f"\n📋 Checking {template_name}...")
    
    repo_root = Path(__file__).parent.parent
    xml_path = repo_root / config['xml_path']
    
    if not xml_path.exists():
        print(f"  ❌ Template file not found: {xml_path}")
        return False
    
    # Fetch upstream docker-compose
    print(f"  🔍 Fetching upstream docker-compose.yml...")
    compose_data = fetch_docker_compose(config['docker_compose_url'])
    
    if not compose_data:
        print(f"  ⚠️  Skipping {template_name} - could not fetch docker-compose.yml")
        return False
    
    # Extract service configuration
    service_config = extract_service_config(compose_data)
    if not service_config:
        print(f"  ⚠️  Could not extract service configuration")
        return False
    
    upstream_env_vars = service_config['environment']
    print(f"  ✅ Found {len(upstream_env_vars)} environment variable(s) in upstream")
    
    # Parse template
    tree = parse_template_xml(xml_path)
    root = tree.getroot()
    template_env_vars = get_template_env_vars(tree)
    print(f"  📄 Template has {len(template_env_vars)} environment variable(s)")
    
    # Find new variables
    new_vars = []
    for var_name, var_value in upstream_env_vars.items():
        # Skip common variables that might differ between docker-compose and template
        if var_name in ['TZ', 'PUID', 'PGID']:
            continue
        
        if var_name not in template_env_vars:
            new_vars.append((var_name, var_value))
    
    if new_vars:
        print(f"  🆕 Found {len(new_vars)} new variable(s):")
        for var_name, var_value in new_vars:
            print(f"     - {var_name} = {var_value}")
            # Determine if variable should be masked (contains SECRET, PASSWORD, KEY, TOKEN)
            mask = "true" if any(keyword in var_name.upper() for keyword in ['SECRET', 'PASSWORD', 'KEY', 'TOKEN', 'API']) else "false"
            # Determine if variable should be required
            required = "true" if var_value == "" else "false"
            # Add to template
            add_env_var_to_template(root, var_name, str(var_value), f"Environment variable: {var_name}", "advanced", required, mask)
        
        # Save updated template
        # Format XML with proper indentation
        ET.indent(tree, space='  ')
        tree.write(xml_path, encoding='utf-8', xml_declaration=True)
        print(f"  ✅ Updated {xml_path}")
        return True
    else:
        print(f"  ✅ Template is up to date")
        return False

def main():
    """Main function"""
    print("🔄 Starting template update check...\n")
    
    updated_templates = []
    
    for template_name, config in TEMPLATE_CONFIGS.items():
        try:
            if update_template(template_name, config):
                updated_templates.append(template_name)
        except Exception as e:
            print(f"  ❌ Error updating {template_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    if updated_templates:
        print(f"✅ Updated {len(updated_templates)} template(s):")
        for name in updated_templates:
            print(f"   - {name}")
        print("\n💡 Please review the changes and commit them.")
        sys.exit(0)
    else:
        print("✅ All templates are up to date!")
        sys.exit(0)

if __name__ == '__main__':
    main()
