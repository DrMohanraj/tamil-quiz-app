import os
import sys
import subprocess
import csv
import random
from flask import Flask, render_template, jsonify, request

def install_package(package_name):
    python_exe = sys.executable.replace("pythonw.exe", "python.exe")
    subprocess.check_call([python_exe, "-m", "pip", "install", package_name])

try:
    import flask
except ImportError:
    install_package("flask")
    import flask

try:
    from tamil import utf8
except ImportError:
    install_package("open-tamil")
    from tamil import utf8

if not os.path.exists('templates'):
    os.makedirs('templates')

# --- USER'S NEW STITCH UI + BACKEND LOGIC ---
html_content = """
<!DOCTYPE html>
<html class="light" lang="ta">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0, viewport-fit=cover" name="viewport"/>
    <title>சொல்-களஞ்சியம் - விளையாடு</title>
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    
    <style>
        /* கொற்கை எழுத்துரு (நீங்கள் முன்பு கேட்டது) */
        @font-face {
            font-family: 'Korkai';
            src: url("{{ url_for('static', filename='fonts/Korkai-Black.ttf') }}") format('truetype');
            font-weight: 900;
        }

        .material-symbols-outlined {
            font-family: 'Material Symbols Outlined' !important; 
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        .letter-glow {
            transition: all 0.2s ease;
            cursor: pointer;
        }
        .letter-glow:active {
            filter: brightness(1.1);
            transform: scale(0.92);
        }
        .bento-card {
            box-shadow: 0px 4px 20px rgba(29, 53, 87, 0.08);
            transition: all 0.3s ease;
        }
        .bento-card:hover {
            box-shadow: 0px 12px 32px rgba(29, 53, 87, 0.12);
        }
        body { min-height: max(884px, 100dvh); font-family: 'Korkai', 'Noto Sans Tamil', sans-serif; }
        .blank { color: #db313f; font-weight: bold; text-decoration: underline; }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-8px); }
            50% { transform: translateX(8px); }
            75% { transform: translateX(-8px); }
        }
        .shake-error {
            animation: shake 0.4s ease-in-out;
            background-color: #ba1a1a !important; 
            color: white !important;
        }
    </style>
    
    <script id="tailwind-config">
        tailwind.config = {
          darkMode: "class",
          theme: {
            extend: {
              "colors": {
                      "on-tertiary-fixed": "#00201d", "inverse-primary": "#ffb3b1", "tertiary": "#006860",
                      "surface-container-high": "#dee8ff", "tertiary-fixed-dim": "#6fd8cc", "tertiary-container": "#008379",
                      "surface-container-lowest": "#ffffff", "primary-fixed-dim": "#ffb3b1", "primary-container": "#db313f",
                      "secondary-fixed-dim": "#98cdf2", "on-background": "#001b3c", "primary": "#b7102a",
                      "on-error": "#ffffff", "surface-container-highest": "#d5e3ff", "surface-container-low": "#f0f3ff",
                      "inverse-surface": "#183153", "background": "#f9f9ff", "surface-dim": "#c8dbff",
                      "on-primary-container": "#fffbff", "on-secondary-container": "#255f80", "on-secondary": "#ffffff",
                      "on-primary-fixed": "#410007", "tertiary-fixed": "#8cf4e8", "secondary-container": "#a3d8fe",
                      "on-error-container": "#93000a", "on-secondary-fixed-variant": "#064c6b", "secondary-fixed": "#c7e7ff",
                      "on-tertiary-container": "#f3fffc", "error": "#ba1a1a", "surface-variant": "#d5e3ff",
                      "on-primary": "#ffffff", "primary-fixed": "#ffdad8", "outline": "#8f6f6e",
                      "on-secondary-fixed": "#001e2e", "outline-variant": "#e4bebc", "surface-container": "#e7eeff",
                      "surface": "#f9f9ff", "on-tertiary-fixed-variant": "#00504a", "secondary": "#2b6485",
                      "on-tertiary": "#ffffff", "surface-tint": "#bb152c", "on-surface-variant": "#5b403f",
                      "on-primary-fixed-variant": "#92001c", "error-container": "#ffdad6", "surface-bright": "#f9f9ff",
                      "inverse-on-surface": "#ecf1ff", "on-surface": "#001b3c"
              },
              "borderRadius": { "DEFAULT": "0.25rem", "lg": "0.5rem", "xl": "0.75rem", "full": "9999px" },
              "spacing": { "gutter": "16px", "sm": "12px", "base": "4px", "xs": "8px", "xl": "32px", "md": "16px", "margin-mobile": "20px", "lg": "24px", "margin-desktop": "64px" },
              "fontFamily": { "headline-md": ["Korkai", "Noto Sans Tamil"], "headline-lg": ["Korkai", "Noto Sans Tamil"], "display-lg": ["Korkai", "Noto Sans Tamil"] }
            }
          }
        }
    </script>
</head>
<body class="bg-background text-on-surface overflow-x-hidden pb-24">

<header class="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-margin-mobile h-16 shadow-sm bg-surface">
    <div class="flex items-center gap-md">
        <span class="material-symbols-outlined text-primary" data-icon="menu">menu</span>
        <h1 class="text-2xl font-bold text-primary">சொல்-களஞ்சியம்</h1>
    </div>
    <div class="bg-secondary-container px-3 py-1 rounded-full flex items-center gap-xs">
        <span class="text-sm font-bold text-on-secondary-container">🏆 <span id="score-display">0</span></span>
    </div>
</header>

<main class="mt-20 px-margin-mobile flex flex-col gap-lg max-w-[800px] mx-auto">
    
    <section id="setup-area" class="bento-card bg-surface-container-lowest p-md rounded-xl flex flex-col gap-md border-t-4 border-secondary">
        <div class="flex flex-col md:flex
