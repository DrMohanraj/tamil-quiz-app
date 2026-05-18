import os
import sys
import subprocess
import csv
import random

# 1. IDLE (pythonw.exe) பிழையைத் தவிர்த்து Flask-ஐ நிறுவும் புதிய மேஜிக் கோட்
def install_package(package_name):
    # pythonw.exe பிழையைத் தவிர்க்க python.exe-ஐப் பயன்படுத்துதல்
    python_exe = sys.executable.replace("pythonw.exe", "python.exe")
    subprocess.check_call([python_exe, "-m", "pip", "install", package_name])

try:
    import flask
except ImportError:
    print("இணையதளத்திற்கான Flask பேக்கேஜ் இன்ஸ்டால் ஆகிறது. காத்திருக்கவும்...")
    install_package("flask")
    print("Flask வெற்றிகரமாக நிறுவப்பட்டது!\n")
    import flask

try:
    from tamil import utf8
except ImportError:
    install_package("open-tamil")
    from tamil import utf8

from flask import Flask, render_template, jsonify

# 2. HTML இணையதள வடிவமைப்பைத் தானாக உருவாக்குதல் (Wordwall Style)
if not os.path.exists('templates'):
    os.makedirs('templates')

html_content = """
html_content = """
<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>சொல்-களஞ்சியம்</title>
    
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;600;700&display=swap" rel="stylesheet">
    
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    
    <style>
        body {
            font-family: 'Noto Sans Tamil', sans-serif;
            background-color: #e0f2f1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 30px;
            max-width: 600px;
        }
        .sentence { 
            font-size: 24px; 
            margin-bottom: 20px; 
            line-height: 2;
            color: #333;
        }
        .dropzone {
            display: inline-block;
            min-width: 150px;
            height: 40px;
            border: 2px dashed #00796b;
            border-radius: 8px;
            vertical-align: middle;
            background-color: #f1f8e9;
            transition: all 0.3s;
            font-weight: bold;
            color: #00796b;
        }
        .options { 
            display: flex; 
            gap: 15px; 
            justify-content: center; 
            flex-wrap: wrap;
        }
        .option {
            background: linear-gradient(135deg, #00796b, #004d40);
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 18px;
            user-select: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            transition: transform 0.2s;
        }
        .option:hover {
            transform: translateY(-3px);
        }

        /* Animations */
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        @keyframes pop {
            0% { transform: scale(1); }
            50% { transform: scale(1.15); }
            100% { transform: scale(1); }
        }
        
        .wrong { 
            animation: shake 0.4s ease-in-out; 
            border-color: #f44336; 
            background-color: #ffebee; 
            color: #f44336;
        }
        .correct { 
            animation: pop 0.4s ease-in-out; 
            border-color: #4CAF50; 
            background-color: #e8f5e9; 
            color: #4CAF50;
        }
    </style>
</head>
<body>

    <div class="card">
        <h2 style="color: #00796b; margin-bottom: 30px;">சரியான விடையை இழுத்து வைக்கவும்</h2>
        <div class="sentence">
            தமிழ் மொழியின் மிகப்பழமையான இலக்கண நூல் <span class="dropzone" id="drop-box" ondrop="drop(event)" ondragover="allowDrop(event)"></span>
        </div>
    </div>

    <div class="options">
        <div class="option" draggable="true" ondragstart="drag(event)" id="opt1">சிலப்பதிகாரம்</div>
        <div class="option" draggable="true" ondragstart="drag(event)" id="opt2">தொல்காப்பியம்</div>
        <div class="option" draggable="true" ondragstart="drag(event)" id="opt3">திருக்குறள்</div>
    </div>

    <script>
        function allowDrop(ev) {
            ev.preventDefault();
        }

        function drag(ev) {
            ev.dataTransfer.setData("text", ev.target.innerText);
        }

        function drop(ev) {
            ev.preventDefault();
            var data = ev.dataTransfer.getData("text");
            var dropBox = document.getElementById("drop-box");
            
            dropBox.innerText = data;

            // விடையைச் சரிபார்த்தல்
            if (data === "தொல்காப்பியம்") {
                dropBox.classList.remove("wrong");
                dropBox.classList.add("correct");
                
                // வெற்றிப் பூக்கள் (Confetti) அனிமேஷன்
                confetti({
                    particleCount: 150,
                    spread: 70,
                    origin: { y: 0.6 },
                    colors: ['#4CAF50', '#00796b', '#FFC107']
                });
            } else {
                dropBox.classList.remove("correct");
                dropBox.classList.add("wrong");
                
                // தவறான விடை என்றால் 1 வினாடியில் பழைய நிலைக்குத் திரும்பும்
                setTimeout(() => {
                    dropBox.innerText = "";
                    dropBox.classList.remove("wrong");
                }, 1000); 
            }
        }
    </script>

</body>
</html>
"""