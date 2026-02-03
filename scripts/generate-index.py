#!/usr/bin/env python3
"""
Automatically generates an index.html for GitHub Pages
based on available XML templates in the repository.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import re

def parse_template(xml_path):
    """Parse XML template and extract metadata"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        return {
            'name': root.findtext('Name', 'Unknown'),
            'description': root.findtext('Overview', 'No description available'),
            'repository': root.findtext('Repository', ''),
            'webui': root.findtext('WebUI', ''),
            'project': root.findtext('Project', ''),
            'icon': root.findtext('Icon', ''),
            'network': root.findtext('Network', 'bridge'),
        }
    except Exception as e:
        print(f"Error parsing {xml_path}: {e}")
        return None

def find_templates():
    """Find all XML templates in the repository"""
    templates = []
    repo_root = Path(__file__).parent.parent
    templates_dir = repo_root / 'templates'
    
    # Find all .xml files in templates directory
    if templates_dir.exists():
        for xml_file in templates_dir.rglob('*.xml'):
            if 'blank-template' in xml_file.name:
                continue
                
            relative_path = xml_file.relative_to(repo_root)
            metadata = parse_template(xml_file)
            
            if metadata:
                templates.append({
                    'path': str(relative_path).replace('\\', '/'),
                    'filename': xml_file.name,
                    'metadata': metadata
                })
    
    return templates

def generate_template_card(template):
    """Generate HTML for a single template card"""
    meta = template['metadata']
    port = meta['webui'].split(':')[-1].replace(']', '') if meta['webui'] else 'N/A (headless)'
    image = meta['repository'].split(':')[0] if meta['repository'] else 'N/A'
    
    # Check for local logo file if no icon is defined in XML
    icon_url = meta['icon']
    if not icon_url:
        # Get template directory
        template_path = Path(template['path'])
        template_dir = template_path.parent
        
        # Check for common image formats
        for ext in ['png', 'svg', 'jpg', 'jpeg', 'webp', 'ico']:
            logo_file = Path(__file__).parent.parent / template_dir / f'logo.{ext}'
            if logo_file.exists():
                # Use raw GitHub URL for the logo
                icon_url = f"https://raw.githubusercontent.com/fgrfn/unraid-templates/main/{template_dir}/logo.{ext}"
                break
    
    # Generate both URLs
    github_pages_url = f"https://fgrfn.github.io/unraid-templates/{template['path']}"
    raw_url = f"https://raw.githubusercontent.com/fgrfn/unraid-templates/main/{template['path']}"
    
    # Generate icon HTML with fallback to DiceBear avatars
    icon_html = ''
    if icon_url:
        # Use provided icon with fallback
        project_name_encoded = meta['name'].replace(' ', '+')
        fallback_icon = f'https://api.dicebear.com/7.x/initials/svg?seed={project_name_encoded}&backgroundColor=667eea,764ba2&textColor=ffffff'
        icon_html = f'<img src="{icon_url}" alt="{meta["name"]}" class="template-icon" style="width: 36px !important; height: 36px !important; max-width: 36px !important; max-height: 36px !important; object-fit: contain;" onerror="this.onerror=null; this.src=\'{fallback_icon}\';">'
    else:
        # Generate avatar based on project name
        project_name_encoded = meta['name'].replace(' ', '+')
        avatar_url = f'https://api.dicebear.com/7.x/initials/svg?seed={project_name_encoded}&backgroundColor=667eea,764ba2&textColor=ffffff'
        icon_html = f'<img src="{avatar_url}" alt="{meta["name"]}" class="template-icon" style="width: 36px !important; height: 36px !important; max-width: 36px !important; max-height: 36px !important; object-fit: contain;">'
    
    project_button = ''
    if meta['project']:
        project_button = f'''
            <a href="{meta['project']}" class="btn btn-secondary" target="_blank">
              📂 Original Project
            </a>
            <a href="{meta['project']}/issues" class="btn btn-link" target="_blank">
              🛟 Support
            </a>'''
    
    return f'''
      <!-- {meta['name']} -->
      <div class="template-card">
        <div class="template-header">
          {icon_html}
          <h2>{meta['name']}</h2>
          <div class="subtitle">{meta['name']} Container</div>
        </div>
        
        <div class="template-body">
          <p class="template-description">
            {meta['description'][:280]}{'...' if len(meta['description']) > 280 else ''}
          </p>
          
          <div class="template-info">
            <div class="info-row">
              <span class="info-label">🌐 WebUI Port:</span>
              <span class="info-value">{port}</span>
            </div>
            <div class="info-row">
              <span class="info-label">📦 Image:</span>
              <span class="info-value">{image}</span>
            </div>
            <div class="info-row">
              <span class="info-label">🔧 Network:</span>
              <span class="info-value">{meta['network']}</span>
            </div>
          </div>
          
          <div class="button-group">
            <a href="{github_pages_url}" class="btn btn-primary" download>
              ⬇️ Download Template
            </a>
            {project_button}
          </div>
          
          <div class="code-box">
            <strong>Quick Install (Unraid GUI):</strong>
            {github_pages_url}
          </div>
          
          <div class="code-box">
            <strong>wget Install (SSH/Terminal):</strong>
            wget -P /boot/config/plugins/dockerMan/templates-user/ {raw_url}
          </div>
        </div>
      </div>'''

def get_html_template():
    """Return the complete HTML template with CSS"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>fgrfn Unraid Templates</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
      color: #333;
    }
    
    .container {
      max-width: 95%;
      margin: 0 auto;
      padding: 0 20px;
    }
    
    header {
      text-align: center;
      color: white;
      margin-bottom: 40px;
      padding: 40px 20px;
    }
    
    header h1 {
      font-size: 3em;
      margin-bottom: 10px;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    header p {
      font-size: 1.2em;
      opacity: 0.9;
    }
    
    .template-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 25px;
      align-items: stretch;
    }
    
    @media (min-width: 1400px) {
      .template-grid {
        grid-template-columns: repeat(4, 1fr);
      }
    }
    
    @media (min-width: 1100px) and (max-width: 1399px) {
      .template-grid {
        grid-template-columns: repeat(3, 1fr);
      }
    }
    
    @media (min-width: 768px) and (max-width: 1099px) {
      .template-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }
    
    @media (max-width: 767px) {
      .template-grid {
        grid-template-columns: 1fr;
      }
      margin-bottom: 40px;
    }
    
    .template-card {
      background: white;
      border-radius: 14px;
      overflow: hidden;
      box-shadow: 0 8px 30px rgba(0,0,0,0.2);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      display: flex;
      flex-direction: column;
      height: 100%;
    }
    
    .template-card:hover {
      transform: translateY(-8px);
      box-shadow: 0 15px 50px rgba(0,0,0,0.3);
    }
    
    .template-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 20px;
      color: white;
      position: relative;
      flex-shrink: 0;
    }
    
      min-height: 0;
    .template-icon {
      width: 36px;
      height: 36px;
      min-width: 36px;
      min-height: 36px;
      max-width: 36px;
      max-height: 36px;
      border-radius: 6px;
      margin-bottom: 10px;
      background: white;
      padding: 3px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.12);
      object-fit: contain;
      object-position: center;
      display: block;
    }
    
    .template-header h2 {
      font: 0 1 autoem;
      margin-bottom: 6px;
    }
    
    .template-header .subtitle {
      opacity: 0.9;
      font-size: 0.85em;
    }
    
    .template-body {
      padding: 20px;
      display: flex;
      flex-direction: column;
      flex: 1;
    }
    
    .template-description {
      color: #555;
      line-height: 1.5;
      margin-bottom: 18px;
      font-size: 0.95em;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      flex-shrink: 0;
    }
    
    .template-info {
      background: #f8f9fa;
      border-radius: 10px;
      padding: 15px;auto
      margin-bottom: 18px;
      flex-shrink: 0;
    }
    
    .info-row {
      display: flex;
      align-items: center;
      margin-bottom: 10px;
      font-size: 0.88em;
      gap: 12px;
    }
    
    .info-row:last-child {
      margin-bottom: 0;
    }
    
    .info-label {
      font-weight: 600;
      color: #667eea;
      min-width: 100px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .info-value {
      color: #333;
      flex: 1;
      font-family: 'Courier New', monospace;
      font-size: 0.9em;
    }
    
    .button-group {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 12px;
      flex-shrink: 0;
    }
    
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 10px 14px;
      text-decoration: none;
      border-radius: 8px;
      font-weight: 600;
      transition: all 0.3s ease;
      text-align: center;
      font-size: 0.85em;
    }
    
    .btn-primary {
      background: #667eea;
      color: white;
      grid-column: 1 / -1;
    }
    
    .btn-primary:hover {
      background: #5568d3;
      transform: scale(1.02);
    }
    
    .btn-secondary {
      background: #f0f0f0;
      color: #333;
    }
    
    .btn-secondary:hover {
      background: #e0e0e0;
    }
    
    .btn-link {
      background: #e8eaf6;
      color: #667eea;
    }
    
    .btn-link:hover {
      background: #d1d5f7;
    }
    
    .quick-install {
      background: white;
      border-radius: 16px;
      padding: 30px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.2);
      margin-bottom: 30px;
    }
    
    .quick-install h2 {
      color: #667eea;
      margin-bottom: 20px;
      font-size: 1.8em;
    }
    
    .install-method {
      margin-bottom: 30px;
    }
    
    .install-method:last-child {
      margin-bottom: 0;
    }
    
    .install-method h3 {
      color: #333;
      margin-bottom: 12px;
      font-size: 1.3em;
    }
    
    .install-method p {
      color: #666;
      margin-bottom: 12px;
      line-height: 1.6;
    }
    
    .code-box {
      background: #f5f5f5;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      padding: 12px;
      font-family: 'Courier New', monospace;
      font-size: 0.75em;
      overflow-x: hidden;
      overflow-wrap: break-word;
      word-break: break-all;
      color: #333;
      position: relative;
      line-height: 1.5;
      margin-bottom: 12px;
      min-height: 70px;
      display: flex;
      flex-direction: column;
    }
    
    .code-box:last-child {
      margin-bottom: 0;
    }
    
    .code-box strong {
      display: block;
      margin-bottom: 8px;
      color: #667eea;
      word-break: normal;
    }
    
    footer {
      text-align: center;
      color: white;
      padding: 30px 20px;
      opacity: 0.9;
    }
    
    footer a {
      color: white;
      text-decoration: underline;
      font-weight: 600;
    }
    
    footer a:hover {
      opacity: 0.8;
    }
    
    @media (max-width: 768px) {
      header h1 {
        font-size: 2em;
      }
      
      .template-grid {
        grid-template-columns: 1fr;
      }
      
      .button-group {
        grid-template-columns: 1fr;
      }
      
      .btn-primary {
        grid-column: 1;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🧰 fgrfn Unraid Templates</h1>
      <p>Curated Docker templates for Unraid – Easy installation & automatic updates</p>
    </header>
    
    <div class="template-grid">
      {TEMPLATE_CARDS}
    </div>
    
    <div class="quick-install">
      <h2>🚀 Installation Methods</h2>
      
      <div class="install-method">
        <h3>Method 1: Quick Install (Recommended)</h3>
        <p>Direct template installation via Unraid GUI:</p>
        <ol style="color: #666; line-height: 1.8; padding-left: 20px;">
          <li>Open Unraid: <strong>Docker → Add Container</strong></li>
          <li>Click on <strong>"Template repositories"</strong> at the top</li>
          <li>Copy & paste the <strong>Quick Install URL</strong> from any template above</li>
          <li>Click <strong>"Add"</strong>, then <strong>"Apply"</strong></li>
        </ol>
      </div>
      
      <div class="install-method">
        <h3>Method 2: Add Repository</h3>
        <p>Get all templates automatically:</p>
        <div class="code-box" style="margin-top: 12px;">
          https://github.com/fgrfn/unraid-templates
        </div>
        <ol style="color: #666; line-height: 1.8; padding-left: 20px; margin-top: 12px;">
          <li>Open Unraid: <strong>Docker → Add Container</strong></li>
          <li>Click <strong>Template repositories</strong> (settings icon)</li>
          <li>Add the repository URL above</li>
          <li>Save and browse all available templates</li>
        </ol>
      </div>
      
      <div class="install-method">
        <h3>Method 3: Manual Download (wget)</h3>
        <p>Each template card above includes its own wget command for quick terminal installation.</p>
        <p style="margin-top: 8px;">After running wget, refresh the Docker page in Unraid to see the new templates.</p>
      </div>
      
    </div>
    
    <footer>
      <p>
        <a href="https://github.com/fgrfn/unraid-templates" target="_blank">📂 View on GitHub</a> • 
        <a href="https://github.com/fgrfn/unraid-templates/issues" target="_blank">🐛 Report Issues</a> • 
        <a href="https://github.com/fgrfn" target="_blank">👤 @fgrfn</a>
      </p>
      <p style="margin-top: 15px; font-size: 0.9em;">
        Made with ❤️ for the Unraid community
      </p>
    </footer>
  </div>
</body>
</html>'''

def generate_blank_template_card():
    """Generate the blank template card"""
    return '''
      <!-- Blank Template -->
      <div class="template-card">
        <div class="template-header">
          <div style="width: 60px; height: 60px; border-radius: 12px; margin-bottom: 12px; background: white; padding: 15px; box-shadow: 0 3px 10px rgba(0,0,0,0.15); display: flex; align-items: center; justify-content: center; font-size: 2em;">
            📝
          </div>
          <h2>Blank Template</h2>
          <div class="subtitle">Starter Template</div>
        </div>
        
        <div class="template-body">
          <p class="template-description">
            Comprehensive starter template with all essential fields, examples, and documentation. 
            Perfect for converting Docker-Compose files or creating custom Unraid templates from scratch.
          </p>
          
          <div class="template-info">
            <div class="info-row">
              <span class="info-label">📋 Includes:</span>
              <span class="info-value">Ports, Volumes, Env Vars</span>
            </div>
            <div class="info-row">
              <span class="info-label">🎯 Use Case:</span>
              <span class="info-value">Template Creation</span>
            </div>
            <div class="info-row">
              <span class="info-label">📖 Documentation:</span>
              <span class="info-value">Inline Comments</span>
            </div>
          </div>
          
          <div class="button-group">
            <a href="https://raw.githubusercontent.com/fgrfn/unraid-templates/main/templates/blank-template.xml" class="btn btn-primary" download>
              ⬇️ Download Template
            </a>
            <a href="https://github.com/fgrfn/unraid-templates/blob/main/templates/blank-template.xml" class="btn btn-secondary" target="_blank">
              👁️ View on GitHub
            </a>
            <a href="https://github.com/fgrfn/unraid-templates" class="btn btn-link" target="_blank">
              📚 Documentation
            </a>
          </div>
          
          <div class="code-box">
            <strong>Raw URL:</strong>
            https://raw.githubusercontent.com/fgrfn/unraid-templates/main/templates/blank-template.xml
            
            <strong style="margin-top: 12px;">wget Install (SSH/Terminal):</strong>
            wget -P /boot/config/plugins/dockerMan/templates-user/ \\<br>
            &nbsp;&nbsp;https://raw.githubusercontent.com/fgrfn/unraid-templates/main/templates/blank-template.xml
          </div>
        </div>
      </div>'''

def main():
    """Main function"""
    print("🔍 Searching for templates...")
    templates = find_templates()
    print(f"✅ Found {len(templates)} template(s)")
    
    if templates:
        for t in templates:
            print(f"   - {t['metadata']['name']} ({t['path']})")
    
    print("\n🔨 Generating HTML...")
    
    # Generate template cards
    template_cards = '\n'.join([generate_template_card(t) for t in templates])
    template_cards += '\n' + generate_blank_template_card()
    
    # Generate complete HTML
    html = get_html_template().replace('{TEMPLATE_CARDS}', template_cards)
    
    # Write to docs/index.html
    docs_dir = Path(__file__).parent.parent / 'docs'
    docs_dir.mkdir(exist_ok=True)
    
    output_file = docs_dir / 'index.html'
    output_file.write_text(html, encoding='utf-8')
    print(f"✅ Generated: {output_file}")

if __name__ == '__main__':
    main()
