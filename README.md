# fgrfn Unraid Templates

Welcome to the central repository for all my personally maintained **Unraid Docker Templates**. 

These templates can be conveniently loaded and automatically updated via the Unraid GUI – hosted via GitHub Pages.

---

## 📦 Available Templates

### 🖨️ Bambuddy

- **Description:** Self-hosted print archive and management system for Bambu Lab 3D printers
- **Template XML:** [`my-Bambuddy.xml`](https://fgrfn.github.io/unraid-templates/templates/Bambuddy/my-Bambuddy.xml)
- **Docker Image:** [`ghcr.io/maziggy/bambuddy`](https://github.com/maziggy/bambuddy)
- **WebUI Port:** 8000
- **Original Project:** [maziggy/bambuddy](https://github.com/maziggy/bambuddy)

**Quick Install:**
```
https://fgrfn.github.io/unraid-templates/templates/Bambuddy/my-Bambuddy.xml
```

### 🖨️ Scan2Target

- **Description:** Modern web-based scan server for network and USB scanners
- **Template XML:** [`my-Scan2Target.xml`](https://fgrfn.github.io/unraid-templates/templates/Scan2Target/my-Scan2Target.xml)
- **Docker Image:** [`ghcr.io/fgrfn/scan2target`](https://github.com/fgrfn/Scan2Target)
- **WebUI Port:** 8000
- **Project:** [fgrfn/Scan2Target](https://github.com/fgrfn/Scan2Target)

**Quick Install:**
```
https://fgrfn.github.io/unraid-templates/templates/Scan2Target/my-Scan2Target.xml
```

### 📊 Netzbremse

- **Description:** Automated speedtest runner for testing peering bottlenecks from Deutsche Telekom connections
- **Template XML:** [`my-Netzbremse.xml`](https://fgrfn.github.io/unraid-templates/templates/Netzbremse/my-Netzbremse.xml)
- **Docker Image:** [`ghcr.io/akvorrat/netzbremse-measurement`](https://github.com/AKVorrat/netzbremse-measurement)
- **WebUI Port:** N/A (headless)
- **Original Project:** [AKVorrat/netzbremse-measurement](https://github.com/AKVorrat/netzbremse-measurement)

**Quick Install:**
```
https://fgrfn.github.io/unraid-templates/templates/Netzbremse/my-Netzbremse.xml
```

---

## 📝 Blank Template

A **template file** is available for quickly creating new templates:

- **Template:** [`blank-template.xml`](https://github.com/fgrfn/unraid-templates/blob/main/templates/blank-template.xml)
- Contains all important fields with examples for ports, volumes, and environment variables
- Perfect for converting Docker-Compose files to Unraid templates

---

## 🌐 GitHub Pages Overview

Central landing page with link index:  
➡️ [`https://fgrfn.github.io/unraid-templates/`](https://fgrfn.github.io/unraid-templates/)

---

## 🛠️ Installation Methods

### Method 1: Quick Install (Single Template)

1. Open Unraid: **Docker → Add Container**
2. Select at the top: **Template repositories**
3. Copy & paste the template URL from the "Quick Install" section above
4. Click **"Add"**, then **"Apply"**

### Method 2: Add Template Repository

Add this repository URL to automatically get all templates: 

```
https://github.com/fgrfn/unraid-templates
```

1. Open Unraid: **Docker → Add Container**
2. Click **Template repositories** (or settings icon)
3. Add the repository URL above
4. Save and browse all available templates

### Method 3: Manual Installation

**Option A: Download via Browser**
1. Download the desired `.xml` file from this repository
2. Place it in `/boot/config/plugins/dockerMan/templates-user/`
3. Refresh the Docker page in Unraid
4. The template will appear in your template list

**Option B: Download via wget (SSH/Terminal)**

Open Unraid terminal or SSH and run: 

```bash
# For Bambuddy template: 
wget -P /boot/config/plugins/dockerMan/templates-user/ https://raw.githubusercontent.com/fgrfn/unraid-templates/main/templates/Bambuddy/my-Bambuddy.xml

# For Scan2Target template:
wget -P /boot/config/plugins/dockerMan/templates-user/ https://raw.githubusercontent.com/fgrfn/unraid-templates/main/templates/Scan2Target/my-Scan2Target.xml

# For Netzbremse template:
wget -P /boot/config/plugins/dockerMan/templates-user/ https://raw.githubusercontent.com/fgrfn/unraid-templates/main/templates/Netzbremse/my-Netzbremse.xml

# For blank template:
wget -P /boot/config/plugins/dockerMan/templates-user/ https://raw.githubusercontent.com/fgrfn/unraid-templates/main/templates/blank-template.xml
```

Then refresh the Docker page in Unraid to see the new template.

---

## ✍️ Contributing

Want to add or improve a template?  
Pull requests are welcome – or contact me directly!

Use [`blank-template.xml`](https://github.com/fgrfn/unraid-templates/blob/main/templates/blank-template.xml) as a starting point for new templates.

### 📋 Template Guidelines

When creating or updating templates, please ensure:

1. **Always include an icon** - Icons display in both Unraid UI and on the GitHub Pages website
   - Use HTTPS URLs pointing to image files (PNG, ICO, or SVG)
   - Sources can include:
     - Project favicon: `https://raw.githubusercontent.com/user/repo/main/static/favicon.ico`
     - Project logo (use `?raw=true`): `https://github.com/user/repo/blob/main/logo.png?raw=true`
     - Organization/user avatar: `https://avatars.githubusercontent.com/u/12345678`

2. **Test the icon URL** - Verify the URL is accessible and returns an image before submitting

3. **Validate your template** - Run the validation script to check for issues:
   ```bash
   python scripts/validate-templates.py
   ```
   This ensures your template meets all requirements (including icon URLs).

4. **Run the generation script** - After updating templates, run:
   ```bash
   python scripts/generate-index.py
   ```
   This updates the GitHub Pages site with your changes.

---

## 📄 License

All templates are based on freely accessible projects.   
The templates themselves are licensed under the MIT License.
