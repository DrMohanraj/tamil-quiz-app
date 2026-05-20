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

# --- FULL PRO UI (SIDEBAR, FOOTER, GAME CONTROLS) ---
html_content = """
<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>சொல்-களஞ்சியம்</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <style>
        @font-face {
            font-family: 'Korkai';
            src: url("{{ url_for('static', filename='fonts/Korkai-Black.ttf') }}") format('truetype');
            font-weight: 900;
        }

        body {
            font-family: 'Korkai', sans-serif;
            background: linear-gradient(135deg, #eef2ff 0%, #f3e8ff 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .material-symbols-outlined { 
            font-family: 'Material Symbols Outlined' !important; 
            font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24; 
        }

        .btn-3d-primary { background-color: #6366f1; color: white; box-shadow: 0 6px 0 #4338ca; transition: all 0.1s; }
        .btn-3d-primary:active { transform: translateY(6px); box-shadow: 0 0px 0 #4338ca; }
        .btn-3d-secondary { background-color: #ec4899; color: white; box-shadow: 0 6px 0 #be185d; transition: all 0.1s; }
        .btn-3d-secondary:active { transform: translateY(6px); box-shadow: 0 0px 0 #be185d; }
        .btn-3d-letter { background-color: #ffffff; color: #4f46e5; box-shadow: 0 6px 0 #c7d2fe; border: 2px solid #e0e7ff; transition: all 0.1s; }
        .btn-3d-letter:hover { background-color: #e0e7ff; }
        .btn-3d-letter:active { transform: translateY(6px); box-shadow: 0 0px 0 #c7d2fe; }

        .game-card { background: white; border-radius: 24px; box-shadow: 0 10px 25px rgba(99, 102, 241, 0.1); border: 4px solid white; }
        .blank { color: #ec4899; font-weight: bold; text-decoration: underline; }
        .progress-fill { transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1); }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-8px); }
            50% { transform: translateX(8px); }
            75% { transform: translateX(-8px); }
        }
        .shake-error {
            animation: shake 0.4s ease-in-out;
            background-color: #ef4444 !important; 
            color: white !important;
            box-shadow: 0 6px 0 #b91c1c !important;
            border-color: #ef4444 !important;
        }

        /* Sidebar Transition */
        #sidebar { transition: transform 0.3s ease-in-out; }
        .overlay { background-color: rgba(0,0,0,0.5); transition: opacity 0.3s; }
    </style>
</head>
<body class="text-gray-800">

<header class="flex justify-between items-center w-full px-6 py-4 sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b-2 border-indigo-100 shadow-sm">
    <div class="flex items-center gap-3">
        <button onclick="toggleSidebar()" class="text-indigo-600 hover:text-indigo-800 transition">
            <span class="material-symbols-outlined text-3xl">menu</span>
        </button>
        <span class="material-symbols-outlined text-3xl text-indigo-500 hidden md:block">menu_book</span>
        <h1 class="text-2xl font-extrabold text-indigo-900 tracking-wide">சொல்-களஞ்சியம்</h1>
    </div>
    <div class="flex items-center gap-4">
        <div class="bg-indigo-100 px-4 py-2 rounded-2xl flex items-center gap-2 border-2 border-indigo-200">
            <span class="material-symbols-outlined text-indigo-600">stars</span>
            <span id="score-display" class="font-bold text-indigo-800 text-lg">0</span>
        </div>
    </div>
</header>

<div id="sidebar-overlay" onclick="toggleSidebar()" class="fixed inset-0 overlay hidden z-40"></div>

<nav id="sidebar" class="fixed top-0 left-0 h-full w-72 bg-white shadow-2xl z-50 transform -translate-x-full border-r-2 border-indigo-100 overflow-y-auto">
    <div class="p-6 flex justify-between items-center border-b-2 border-indigo-50 bg-indigo-50">
        <div class="flex items-center gap-2 text-indigo-900">
            <span class="material-symbols-outlined">account_circle</span>
            <span class="font-bold text-lg">kannitamilan1</span>
        </div>
        <button onclick="toggleSidebar()" class="text-gray-500 hover:text-red-500"><span class="material-symbols-outlined">close</span></button>
    </div>
    <ul class="flex flex-col py-4 px-2 space-y-1 text-indigo-700 font-bold">
        <li><a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-indigo-50 transition"><span class="material-symbols-outlined text-blue-500">add</span> Create Activity</a></li>
        <li><a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-indigo-50 transition"><span class="material-symbols-outlined text-blue-500">folder</span> My Activities</a></li>
        <li><a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-indigo-50 transition"><span class="material-symbols-outlined text-blue-500">bar_chart</span> My Results</a></li>
        <li><a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-indigo-50 transition"><span class="material-symbols-outlined text-blue-500">edit</span> Edit Personal Details</a></li>
        <li><a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-indigo-50 transition"><span class="material-symbols-outlined text-blue-500">upgrade</span> Upgrade</a></li>
        <li><a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-indigo-50 transition"><span class="material-symbols-outlined text-blue-500">public</span> Language And Location</a></li>
        <li class="border-b-2 border-gray-100 my-2"></li>
        <li><a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-red-50 text-red-500 transition"><span class="material-symbols-outlined text-red-500">logout</span> Log Out</a></li>
        <li class="border-b-2 border-gray-100 my-2"></li>
        <li><a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-gray-50 text-gray-600 transition"><span class="material-symbols-outlined">search</span> Community</a></li>
        <li><a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-gray-50 text-gray-600 transition"><span class="material-symbols-outlined">mail</span> Contact</a></li>
        <li><a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-gray-50 text-gray-600 transition"><span class="material-symbols-outlined">payments</span> Price Plans</a></li>
    </ul>
</nav>

<main class="max-w-[900px] mx-auto px-4 py-8 space-y-8 flex-grow w-full">
    
    <section id="setup-area" class="game-card p-8 text-center space-y-8 mt-10">
        <div class="space-y-2">
            <span class="material-symbols-outlined text-6xl text-pink-500">rocket_launch</span>
            <h2 class="text-3xl font-extrabold text-indigo-900">விளையாடத் தயாரா?</h2>
            <p class="text-gray-500">உங்கள் வகுப்பு மற்றும் இயலைத் தேர்ந்தெடுங்கள்</p>
        </div>

        <div class="flex flex-col md:flex-row gap-6 justify-center items-center">
            <div class="w-full max-w-xs text-left">
                <label class="text-indigo-800 font-bold ml-2">வகுப்பு</label>
                <select id="class-select" class="w-full mt-2 bg-indigo-50 border-2 border-indigo-200 text-indigo-900 rounded-2xl p-4 appearance-none font-bold outline-none focus:border-indigo-500 text-lg cursor-pointer">
                    <option value="6-ஆம் வகுப்பு">6-ஆம் வகுப்பு</option>
                    <option value="7-ஆம் வகுப்பு">7-ஆம் வகுப்பு</option>
                    <option value="8-ஆம் வகுப்பு">8-ஆம் வகுப்பு</option>
                    <option value="9-ஆம் வகுப்பு">9-ஆம் வகுப்பு</option>
                </select>
            </div>
            <div class="w-full max-w-xs text-left">
                <label class="text-indigo-800 font-bold ml-2">இயல்</label>
                <select id="chapter-select" class="w-full mt-2 bg-indigo-50 border-2 border-indigo-200 text-indigo-900 rounded-2xl p-4 appearance-none font-bold outline-none focus:border-indigo-500 text-lg cursor-pointer">
                    <option value="இயல் 1">இயல் 1</option>
                    <option value="இயல் 2">இயல் 2</option>
                    <option value="இயல் 3">இயல் 3</option>
                    <option value="இயல் 4">இயல் 4</option>
                    <option value="இயல் 5">இயல் 5</option>
                </select>
            </div>
        </div>

        <button onclick="startGame()" class="mt-8 px-12 py-4 rounded-2xl btn-3d-primary text-xl font-bold w-full md:w-auto tracking-wider">
            தொடங்கு <span class="material-symbols-outlined align-middle ml-1">play_arrow</span>
        </button>
    </section>

    <section id="quiz-area" class="game-card p-6 md:p-10 relative pb-20" style="display: none;">
        
        <div class="w-full bg-gray-200 rounded-full h-4 mb-8 border-2 border-gray-300 overflow-hidden relative">
            <div id="progress-bar" class="bg-gradient-to-r from-pink-400 to-pink-600 h-full rounded-full progress-fill" style="width: 0%;"></div>
        </div>

        <div class="flex items-center justify-between mb-6">
            <h2 id="question-text" class="text-2xl font-bold text-indigo-900 bg-indigo-50 px-4 py-2 rounded-xl border border-indigo-100 inline-block">கேள்வி...</h2>
            <div class="flex gap-2">
                <button id="undo-btn" onclick="undoLetter()" class="bg-gray-100 text-gray-600 p-2 rounded-xl border-2 border-gray-200 hover:bg-gray-200" style="display:none;" title="மாற்று">
                    <span class="material-symbols-outlined">undo</span>
                </button>
                <button id="skip-btn" onclick="skipQuestion()" class="bg-red-50 text-red-500 p-2 rounded-xl border-2 border-red-100 hover:bg-red-100" style="display:none;" title="தவிர்">
                    <span class="material-symbols-outlined">skip_next</span>
                </button>
            </div>
        </div>

        <div class="text-center space-y-10 py-4">
            <p id="sentence-text" class="text-2xl md:text-3xl text-gray-700 leading-relaxed font-bold tracking-wide"></p>

            <div id="answer-display" class="flex flex-wrap items-center justify-center gap-3 min-h-[80px]"></div>

            <div id="jumbled-letters-grid" class="flex flex-wrap justify-center gap-4 mt-8 bg-indigo-50 p-6 rounded-3xl border-2 border-indigo-100"></div>
            
            <div id="status-message" class="hidden justify-center items-center gap-2 mt-4">
                <span class="material-symbols-outlined text-4xl text-green-500 animate-bounce">check_circle</span>
                <span class="text-2xl font-bold text-green-600">சரியான விடை!</span>
            </div>

            <button id="next-btn" onclick="fetchQuestion()" class="mx-auto mt-8 px-12 py-4 rounded-2xl btn-3d-secondary text-xl font-bold tracking-wider" style="display: none;">
                அடுத்தது <span class="material-symbols-outlined align-middle ml-1">arrow_forward</span>
            </button>
        </div>

        <div class="absolute bottom-0 left-0 w-full bg-gray-100 border-t-2 border-gray-200 rounded-b-2xl px-4 py-3 flex justify-between items-center text-gray-600 font-bold">
            <button onclick="toggleSidebar()" class="hover:text-indigo-600 transition"><span class="material-symbols-outlined text-2xl">menu</span></button>
            
            <div class="flex items-center gap-2 text-lg">
                <span class="material-symbols-outlined">play_arrow</span>
                <span id="current-q-display">1</span> of <span id="total-q-display">10</span>
            </div>
            
            <div class="flex items-center gap-4">
                <button onclick="toggleMute()" class="hover:text-indigo-600 transition">
                    <span id="volume-icon" class="material-symbols-outlined text-2xl">volume_up</span>
                </button>
                <button onclick="toggleFullScreen()" class="hover:text-indigo-600 transition">
                    <span id="fullscreen-icon" class="material-symbols-outlined text-2xl">fullscreen</span>
                </button>
            </div>
        </div>

    </section>
</main>

<footer class="bg-[#eaf4fa] border-t border-gray-300 w-full pt-10 pb-6 mt-auto font-sans">
    <div class="max-w-[1200px] mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-8 text-[#335c75]">
        <div>
            <h3 class="font-bold text-xl mb
