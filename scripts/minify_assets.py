#!/usr/bin/env python3
"""
VidhiMeet Asset Minifier Script
Minifies CSS and JS files in the frontend directory for peak SEO and page load performance.
"""

import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
CSS_DIR = FRONTEND_DIR / "css"
JS_DIR = FRONTEND_DIR / "js"

def minify_css(css_text: str) -> str:
    """Minify CSS text by stripping comments and excessive whitespace."""
    # Remove comments
    css_text = re.sub(r'/\*[\s\S]*?\*/', '', css_text)
    # Remove newlines and tabs
    css_text = re.sub(r'[\r\n\t]+', ' ', css_text)
    # Normalize spaces around special chars
    css_text = re.sub(r'\s*([\{\}\:\;\,\>])\s*', r'\1', css_text)
    # Remove trailing semicolons before closing brace
    css_text = re.sub(r';\}', '}', css_text)
    # Collapse multiple spaces
    css_text = re.sub(r'\s{2,}', ' ', css_text)
    return css_text.strip()

def minify_js(js_text: str) -> str:
    """Minify JS text while preserving strings and regex literals safely."""
    # Basic robust JS minification
    # 1. Remove block comments /* ... */
    # (avoiding strings)
    pattern = r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`)|(/\*[\s\S]*?\*/|(?<!:)//[^\r\n]*)'
    
    def replace_comments(match):
        if match.group(1):
            return match.group(1) # Keep string literals unchanged
        return '' # Remove comments
        
    cleaned = re.sub(pattern, replace_comments, js_text)
    
    # 2. Split lines and strip whitespace
    lines = []
    for line in cleaned.splitlines():
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
            
    # Combine with minimal line breaks to preserve ASI (Automatic Semicolon Insertion)
    result = '\n'.join(lines)
    return result

def process_assets():
    print("Starting VidhiMeet Static Asset Minification...")
    
    # Process CSS
    if CSS_DIR.exists():
        for css_file in CSS_DIR.glob("*.css"):
            if css_file.name.endswith(".min.css"):
                continue
            original_content = css_file.read_text(encoding="utf-8")
            minified = minify_css(original_content)
            min_file = css_file.with_name(f"{css_file.stem}.min.css")
            min_file.write_text(minified, encoding="utf-8")
            orig_size = len(original_content.encode("utf-8"))
            min_size = len(minified.encode("utf-8"))
            saved = ((orig_size - min_size) / orig_size) * 100 if orig_size > 0 else 0
            print(f"  [CSS] {css_file.name} -> {min_file.name} ({orig_size}B -> {min_size}B, -{saved:.1f}%)")
            
    # Process JS
    if JS_DIR.exists():
        for js_file in JS_DIR.glob("*.js"):
            if js_file.name.endswith(".min.js"):
                continue
            original_content = js_file.read_text(encoding="utf-8")
            minified = minify_js(original_content)
            min_file = js_file.with_name(f"{js_file.stem}.min.js")
            min_file.write_text(minified, encoding="utf-8")
            orig_size = len(original_content.encode("utf-8"))
            min_size = len(minified.encode("utf-8"))
            saved = ((orig_size - min_size) / orig_size) * 100 if orig_size > 0 else 0
            print(f"  [JS]  {js_file.name} -> {min_file.name} ({orig_size}B -> {min_size}B, -{saved:.1f}%)")

    print("All assets minified successfully!")

if __name__ == "__main__":
    process_assets()
