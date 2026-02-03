# Creating a Logo for Netzbremse Template

You can add a custom logo by placing an image file named `logo.png` (or `logo.svg`, `logo.jpg`, etc.) in this directory.

## Quick Logo Creation Options:

### Option 1: Use an online generator
- Visit https://www.favicon-generator.org/
- Create a simple logo with the letter "N"
- Download and save as `logo.png`

### Option 2: Use existing project assets
- Check if the upstream project has a logo
- Download from: https://github.com/AKVorrat/netzbremse-measurement

### Option 3: Simple SVG
Create a file called `logo.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="#667eea"/>
  <text x="50" y="70" font-size="60" fill="white" text-anchor="middle" font-family="Arial" font-weight="bold">N</text>
</svg>
```

After adding the logo file:
1. Commit and push the `logo.svg` or `logo.png` file
2. GitHub Actions will automatically update the website
3. Your logo will appear on https://fgrfn.github.io/unraid-templates/ within minutes
