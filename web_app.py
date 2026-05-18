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

# Google Stitch Design + Dynamic JavaScript
html_content = """
<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>சொல்-களஞ்சியம்</title>
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <script id="tailwind-config">
      tailwind.config = {
        darkMode: "class",
        theme: {
          extend: {
            "colors": {
                    "on-background": "#161d1f",
                    "primary-container": "#008377",
                    "on-primary-fixed": "#00201c",
                    "tertiary-fixed-dim": "#b8cac9",
                    "on-surface": "#161d1f",
                    "on-error": "#ffffff",
                    "tertiary": "#4f5f5f",
                    "surface-dim": "#d4dbdd",
                    "surface-container-highest": "#dde4e6",
                    "on-tertiary-container": "#f3fffe",
                    "on-secondary-fixed-variant": "#693c00",
                    "inverse-surface": "#2b3234",
                    "on-primary-fixed-variant": "#005048",
                    "inverse-on-surface": "#ebf2f4",
                    "secondary-container": "#ff9800",
                    "error-container": "#ffdad6",
                    "tertiary-fixed": "#d4e6e5",
                    "surface": "#f4fafd",
                    "on-tertiary-fixed-variant": "#3a4a49",
                    "background": "#f4fafd",
                    "tertiary-container": "#677877",
                    "surface-container-lowest": "#ffffff",
                    "primary-fixed-dim": "#67d9c9",
                    "on-surface-variant": "#3d4947",
                    "surface-variant": "#dde4e6",
                    "outline-variant": "#bcc9c6",
                    "primary-fixed": "#85f6e5",
                    "surface-bright": "#f4fafd",
                    "on-primary-container": "#f4fffb",
                    "surface-container-high": "#e2e9ec",
                    "on-error-container": "#93000a",
                    "primary": "#00685e",
                    "on-secondary": "#ffffff",
                    "on-tertiary-fixed": "#0e1e1e",
                    "surface-container": "#e8eff1",
                    "inverse-primary": "#67d9c9",
                    "surface-tint": "#006a60",
                    "secondary-fixed": "#ffdcbe",
                    "on-secondary-fixed": "#2c1600",
                    "secondary": "#8b5000",
                    "surface-container-low": "#eef5f7",
                    "on-secondary-container": "#653900",
                    "on-tertiary": "#ffffff",
                    "on-primary": "#ffffff",
                    "outline": "#6d7a77",
                    "error": "#ba1a1a",
                    "secondary-fixed-dim": "#ffb870"
            },
            "fontFamily": {
                    "body-lg": ["Plus Jakarta Sans"],
                    "headline-lg": ["Plus Jakarta Sans"],
                    "body-md": ["Plus Jakarta Sans"],
                    "headline-xl": ["Plus Jakarta Sans"],
                    "label-md": ["Plus Jakarta Sans"],
                    "headline-lg-mobile": ["Plus Jakarta Sans"]
            }
          },
        },
      }
    </script>
    <style>
        .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
        .tactile-btn { box-shadow: 0 4px 0 0 rgba(0, 80, 72, 1); transition: all 0.1s ease; }
        .tactile-btn:active { transform: translateY(4px); box-shadow: 0 0 0 0 rgba(0, 80, 72, 1); }
        .tactile-btn-orange { box-shadow: 0 4px 0 0 rgba(101, 57, 0, 1); transition: all 0.1s ease; }
        .tactile-btn-orange:active { transform: translateY(4px); box-shadow: 0 0 0 0 rgba(101, 57, 0, 1); }
        .blank { color: #008377; font-weight: bold; text-decoration: underline; }
    </style>
</head>
<body class="bg-surface text-on-surface font-body-md min-h-screen pb-24 md:pb-0">

<header class="flex justify-between items-center w-full px-4 py-4 sticky top-0 z-50 bg-surface border-b-2 border-primary/10 shadow-sm">
    <h1 class="font-headline-lg-mobile text-2xl font-extrabold text-primary">📚 சொல்-களஞ்சியம்</h1>
    <div class="flex items-center gap-4">
        <span id="score-display" class="font-label-md text-label-md text-primary bg-primary-container/10 px-4 py-2 rounded-full border border-primary/20">
            மதிப்பெண்: 0
        </span>
    </div>
</header>

<main class="max-w-[1200px] mx-auto px-4 md:px-16 py-8 space-y-8">
    
    <section class="grid grid-cols-1 md:grid-cols-12 gap-6 items-stretch">
        <div class="md:col-span-8 bg-surface-container-lowest rounded-xl p-6 border-2 border-primary/5 shadow-sm">
            <div class="flex flex-col md:flex-row gap-6 items-end">
                <div class="w-full space-y-2">
                    <label class="font-label-md text-label-md text-outline">வகுப்பைத் தேர்ந்தெடு</label>
                    <select id="class-select" class="w-full bg-surface-container-low border-2 border-transparent focus:border-secondary-container rounded-lg p-3 font-body-md appearance-none">
                        <option value="6-ஆம் வகுப்பு">6-ஆம் வகுப்பு</option>
                        <option value="7-ஆம் வகுப்பு">7-ஆம் வகுப்பு</option>
                        <option value="8-ஆம் வகுப்பு">8-ஆம் வகுப்பு</option>
                        <option value="9-ஆம் வகுப்பு">9-ஆம் வகுப்பு</option>
                    </select>
                </div>
                <div class="w-full space-y-2">
                    <label class="font-label-md text-label-md text-outline">இயலைத் தேர்ந்தெடு</label>
                    <select id="chapter-select" class="w-full bg-surface-container-low border-2 border-transparent focus:border-secondary-container rounded-lg p-3 font-body-md appearance-none">
                        <option value="இயல் 1">இயல் 1</option>
                        <option value="இயல் 2">இயல் 2</option>
                        <option value="இயல் 3">இயல் 3</option>
                    </select>
                </div>
                <button onclick="startGame()" class="w-full md:w-auto bg-primary text-on-primary font-label-md text-label-md px-8 py-3.5 rounded-xl tactile-btn whitespace-nowrap">
                    விளையாடத் தொடங்கு
                </button>
            </div>
        </div>
        <div class="md:col-span-4 bg-primary-container text-on-primary-container rounded-xl p-6 relative overflow-hidden flex flex-col justify-center">
            <div class="z-10">
                <h3 class="font-headline-lg-mobile text-headline-lg-mobile mb-1">இன்றைய இலக்கு</h3>
                <p class="font-body-md text-body-md opacity-90">சொற்களைச் சரியாகக் கண்டறிந்து வெற்றி பெறு!</p>
            </div>
            <div class="absolute -right-4 -bottom-4 opacity-20">
                <span class="material-symbols-outlined text-[120px]" data-icon="auto_awesome">auto_awesome</span>
            </div>
        </div>
    </section>

    <section id="quiz-area" class="bg-surface-container-lowest rounded-xl border-2 border-primary/10 shadow-sm overflow-hidden" style="display: none;">
        
        <div class="bg-primary/5 p-4 md:p-6 border-b border-primary/10 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <span class="bg-primary text-on-primary rounded-full p-2 flex items-center justify-center">
                    <span class="material-symbols-outlined text-sm" data-icon="quiz">quiz</span>
                </span>
                <h2 id="question-text" class="font-headline-lg-mobile text-headline-lg-mobile text-primary">கேள்வி ஏற்றப்படுகிறது...</h2>
            </div>
        </div>

        <div class="p-6 md:p-12 space-y-12">
            <div class="text-center space-y-6">
                <div class="inline-block px-4 py-1 bg-secondary-container/10 text-secondary font-label-md text-label-md rounded-full border border-secondary-container/20">
                    வாக்கியத்தை நிரப்புக
                </div>
                <p id="sentence-text" class="font-headline-lg text-2xl text-on-surface leading-relaxed"></p>
            </div>

            <div class="max-w-xl mx-auto space-y-4">
                <div class="flex items-center justify-between px-4">
                    <span class="font-label-md text-label-md text-outline">உன் விடை:</span>
                    <div id="status-icons" class="flex gap-2" style="display:none;">
                        <span id="icon-correct" class="material-symbols-outlined text-green-600" data-icon="check_circle" style="display:none;">check_circle</span>
                        <span id="icon-wrong" class="material-symbols-outlined text-error" data-icon="cancel" style="display:none;">cancel</span>
                    </div>
                </div>
                
                <div id="answer-display" class="bg-surface-container-low border-2 border-primary-container/20 rounded-2xl h-20 flex items-center justify-center gap-3 shadow-inner text-3xl font-bold text-primary">
                    </div>
            </div>

            <div id="jumbled-letters-grid" class="flex flex-wrap justify-center gap-4 max-w-2xl mx-auto">
                </div>

            <div class="flex flex-col md:flex-row items-center justify-center gap-6 pt-8">
                <button id="next-btn" onclick="fetchQuestion()" class="flex items-center gap-3 bg-secondary-container text-on-secondary-container px-10 py-4 rounded-full tactile-btn-orange font-headline-lg-mobile text-headline-lg-mobile group" style="display: none;">
                    அடுத்த கேள்வி
                    <span class="material-symbols-outlined group-hover:translate-x-1 transition-transform" data-icon="arrow_forward">arrow_forward</span>
                </button>
            </div>
        </div>
    </section>

</main>

<audio id="success-sound" src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3"></audio>
<audio id="error-sound" src="https://assets.mixkit.co/active_storage/sfx/2954/2954-preview.mp3"></audio>

<script>
    let currentCorrectWord = "";
    let currentAnswer = "";
    let score = 0;
    let selectedClass = "";
    let selectedChapter = "";

    function startGame() {
        selectedClass = document.getElementById('class-select').value;
        selectedChapter = document.getElementById('chapter-select').value;
        document.getElementById('quiz-area').style.display = 'block';
        fetchQuestion();
    }

    function fetchQuestion() {
        document.getElementById('next-btn').style.display = 'none';
        document.getElementById('answer-display').innerHTML = "";
        document.getElementById('status-icons').style.display = 'none';
        document.getElementById('icon-correct').style.display = 'none';
        document.getElementById('icon-wrong').style.display = 'none';
        currentAnswer = "";
        
        // Sending class and chapter to Python Server
        fetch(`/get_question?vakuppu=${encodeURIComponent(selectedClass)}&iyal=${encodeURIComponent(selectedChapter)}`)
            .then(response => response.json())
            .then(data => {
                if(data.error) {
                    document.getElementById('question-text').innerHTML = "⚠️ " + data.error;
                    document.getElementById('sentence-text').innerHTML = "இந்த இயலில் கேள்விகள் இன்னும் சேர்க்கப்படவில்லை.";
                    document.getElementById('jumbled-letters-grid').innerHTML = "";
                    return;
                }
                
                document.getElementById('question-text').innerHTML = data.question;
                document.getElementById('sentence-text').innerHTML = data.sentence;
                currentCorrectWord = data.correct_word;
                
                let lettersHTML = "";
                let colors = ['bg-primary tactile-btn text-on-primary hover:bg-primary-container', 'bg-secondary-container tactile-btn-orange text-on-secondary-container hover:bg-secondary-fixed'];
                
                data.jumbled_letters.forEach((letter, index) => {
                    let colorClass = colors[index % 2];
                    lettersHTML += `<button class="w-16 h-16 md:w-20 md:h-20 rounded-xl font-headline-lg text-2xl flex items-center justify-center transition-all letter-btn ${colorClass}" onclick="addLetter('${letter}', this)">${letter}</button>`;
                });
                document.getElementById('jumbled-letters-grid').innerHTML = lettersHTML;
            });
    }

    function addLetter(letter, btnElement) {
        currentAnswer += letter;
        
        // Create an attractive box for the clicked letter
        document.getElementById('answer-display').innerHTML += `<div class="w-12 h-12 bg-surface-container-lowest rounded-lg flex items-center justify-center shadow-sm border border-primary/10">${letter}</div>`;
        
        btnElement.style.display = 'none'; 
        
        if (currentAnswer.length === currentCorrectWord.length) {
            document.getElementById('status-icons').style.display = 'flex';
            
            if (currentAnswer === currentCorrectWord) {
                document.getElementById('icon-correct').style.display = 'block';
                document.getElementById('next-btn').style.display = 'flex';
                
                let audio = document.getElementById('success-sound');
                audio.volume = 0.5; audio.play();
                score += 10;
                document.getElementById('score-display').innerText = "மதிப்பெண்: " + score;
                
            } else {
                document.getElementById('icon-wrong').style.display = 'block';
                let errAudio = document.getElementById('error-sound');
                errAudio.volume = 0.5; errAudio.play();
                
                setTimeout(() => {
                    document.getElementById('answer-display').innerHTML = "";
                    document.getElementById('status-icons').style.display = 'none';
                    document.getElementById('icon-wrong').style.display = 'none';
                    currentAnswer = "";
                    let buttons = document.querySelectorAll('.letter-btn');
                    buttons.forEach(btn => btn.style.display = 'flex');
                }, 1500);
            }
        }
    }
</script>
</body>
</html>
"""

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

app = Flask(__name__)
csv_file = "tamil_quiz_data.csv"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_question')
def get_question():
    if not os.path.exists(csv_file):
        return jsonify({"error": "CSV பைல் கிடைக்கவில்லை!"})
        
    vakuppu = request.args.get('vakuppu', '')
    iyal = request.args.get('iyal', '')
        
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        data_list = list(csv_reader)
        
        # Filtering Logic based on dropdown selection
        filtered_data = []
        for row in data_list:
            if row.get('வகுப்பு', '').strip() == vakuppu and row.get('இயல்', '').strip() == iyal:
                filtered_data.append(row)
                
        if not filtered_data:
             return jsonify({"error": f"{vakuppu} - {iyal} இல் தரவுகள் இல்லை!"})
             
        random_row = random.choice(filtered_data)
        
        question = random_row.get('கேள்வி', '')
        full_answer = random_row.get('முழுமையான வாக்கியம் (விடை)', '')
        target_words_str = str(random_row.get('கலைக்கப்பட வேண்டிய சொற்கள்', ''))
        
        target_words = [w.strip() for w in target_words_str.split(',') if w.strip()]
        
        if target_words:
            word_to_jumble = target_words[0]
            letters = utf8.get_letters(word_to_jumble)
            jumbled = letters.copy()
            while jumbled == letters and len(letters) > 1:
                random.shuffle(jumbled)
        else:
            word_to_jumble = "பிழை"
            jumbled = ["பி", "ழை"]

        sentence_with_blank = full_answer.replace(word_to_jumble, "<span class='blank'>________</span>")

        return jsonify({
            'question': question,
            'sentence': sentence_with_blank,
            'jumbled_letters': jumbled,
            'correct_word': word_to_jumble
        })

if __name__ == '__main__':
    app.run(debug=False)
