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

# Google Stitch Design + Korkai Font + Skip Option + Remaining Count + Game Over Screen
html_content = """
<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>சொல்-களஞ்சியம்</title>
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <script id="tailwind-config">
      tailwind.config = {
        darkMode: "class",
        theme: {
          extend: {
            "colors": {
                    "on-background": "#161d1f",
                    "primary-container": "#008377",
                    "surface-container-lowest": "#ffffff",
                    "primary": "#00685e",
                    "secondary-container": "#ff9800",
                    "surface": "#f4fafd",
            },
            "fontFamily": {
                    "body-lg": ["Korkai", "sans-serif"],
                    "headline-lg": ["Korkai", "sans-serif"],
                    "label-md": ["Korkai", "sans-serif"],
                    "body-md": ["Korkai", "sans-serif"],
                    "headline-lg-mobile": ["Korkai", "sans-serif"],
                    "sans": ["Korkai", "sans-serif"]
            }
          },
        },
      }
    </script>
    <style>
        /* கொற்கை எழுத்துரு */
        @font-face {
            font-family: 'Korkai';
            src: url("{{ url_for('static', filename='fonts/Korkai-Black.ttf') }}") format('truetype');
            font-weight: 900;
            font-style: normal;
            font-display: swap;
        }

        .material-symbols-outlined { 
            font-family: 'Material Symbols Outlined' !important; 
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; 
        }

        .tactile-btn { box-shadow: 0 4px 0 0 rgba(0, 80, 72, 1); transition: all 0.1s ease; }
        .tactile-btn:active { transform: translateY(4px); box-shadow: 0 0 0 0 rgba(0, 80, 72, 1); }
        .tactile-btn-orange { box-shadow: 0 4px 0 0 rgba(101, 57, 0, 1); transition: all 0.1s ease; }
        .tactile-btn-orange:active { transform: translateY(4px); box-shadow: 0 0 0 0 rgba(101, 57, 0, 1); }
        .blank { color: #008377; font-weight: bold; text-decoration: underline; }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-6px); }
            50% { transform: translateX(6px); }
            75% { transform: translateX(-6px); }
        }
        .shake-error {
            animation: shake 0.4s ease-in-out;
            background-color: #ef4444 !important; 
            color: white !important;
            box-shadow: 0 4px 0 0 #b91c1c !important;
        }
    </style>
</head>
<body class="bg-surface text-on-surface min-h-screen pb-24 md:pb-0" style="font-family: 'Korkai', sans-serif;">

<header class="flex justify-between items-center w-full px-4 py-4 sticky top-0 z-50 bg-surface border-b-2 border-primary/10 shadow-sm">
    <h1 class="font-headline-lg-mobile text-2xl font-extrabold text-primary">📚 சொல்-களஞ்சியம்</h1>
    <div class="flex items-center gap-3">
        <span id="remaining-display" class="font-label-md text-sm text-orange-800 bg-orange-100 px-3 py-1 rounded-full border border-orange-200" style="display:none;">
            மீதம்: 0
        </span>
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
                    <label class="font-label-md text-label-md text-gray-600">வகுப்பைத் தேர்ந்தெடு</label>
                    <select id="class-select" class="w-full bg-gray-100 border-2 border-transparent focus:border-orange-500 rounded-lg p-3 font-body-md appearance-none">
                        <option value="6-ஆம் வகுப்பு">6-ஆம் வகுப்பு</option>
                        <option value="7-ஆம் வகுப்பு">7-ஆம் வகுப்பு</option>
                        <option value="8-ஆம் வகுப்பு">8-ஆம் வகுப்பு</option>
                        <option value="9-ஆம் வகுப்பு">9-ஆம் வகுப்பு</option>
                    </select>
                </div>
                <div class="w-full space-y-2">
                    <label class="font-label-md text-label-md text-gray-600">இயலைத் தேர்ந்தெடு</label>
                    <select id="chapter-select" class="w-full bg-gray-100 border-2 border-transparent focus:border-orange-500 rounded-lg p-3 font-body-md appearance-none">
                        <option value="இயல் 1">இயல் 1</option>
                        <option value="இயல் 2">இயல் 2</option>
                        <option value="இயல் 3">இயல் 3</option>
                    </select>
                </div>
                <button onclick="startGame()" class="w-full md:w-auto bg-primary text-white font-label-md px-8 py-3.5 rounded-xl tactile-btn whitespace-nowrap">
                    விளையாடத் தொடங்கு
                </button>
            </div>
        </div>
        <div class="md:col-span-4 bg-primary-container text-white rounded-xl p-6 relative overflow-hidden flex flex-col justify-center">
            <div class="z-10">
                <h3 class="text-xl font-bold mb-1">இன்றைய இலக்கு</h3>
                <p class="opacity-90">சொற்களைச் சரியாகக் கண்டறிந்து வெற்றி பெறு!</p>
            </div>
            <div class="absolute -right-4 -bottom-4 opacity-20">
                <span class="material-symbols-outlined text-[120px]" data-icon="auto_awesome">auto_awesome</span>
            </div>
        </div>
    </section>

    <section id="quiz-area" class="bg-surface-container-lowest rounded-xl border-2 border-primary/10 shadow-sm overflow-hidden" style="display: none;">
        
        <div class="bg-primary/5 p-4 md:p-6 border-b border-primary/10 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <span class="bg-primary text-white rounded-full p-2 flex items-center justify-center">
                    <span class="material-symbols-outlined text-sm" data-icon="quiz">quiz</span>
                </span>
                <h2 id="question-text" class="text-xl font-bold text-primary">கேள்வி ஏற்றப்படுகிறது...</h2>
            </div>
        </div>

        <div class="p-6 md:p-12 space-y-12">
            <div class="text-center space-y-6">
                <div class="inline-block px-4 py-1 bg-orange-100 text-orange-800 font-bold rounded-full border border-orange-200">
                    வாக்கியத்தை நிரப்புக
                </div>
                <p id="sentence-text" class="font-headline-lg text-2xl text-gray-800 leading-relaxed"></p>
            </div>

            <div class="max-w-xl mx-auto space-y-4">
                <div class="flex items-center justify-between px-4">
                    <div class="flex items-center gap-2">
                        <span class="font-bold text-gray-600 mr-2">உன் விடை:</span>
                        <button id="undo-btn" onclick="undoLetter()" class="flex items-center gap-1 bg-gray-200 text-gray-700 px-3 py-1 rounded-lg text-sm font-bold hover:bg-gray-300 transition" style="display:none;">
                            <span class="material-symbols-outlined text-[16px]">undo</span> மாற்று
                        </button>
                        <button id="skip-btn" onclick="skipQuestion()" class="flex items-center gap-1 bg-red-100 text-red-700 px-3 py-1 rounded-lg text-sm font-bold hover:bg-red-200 transition" style="display:none;">
                            தவிர் <span class="material-symbols-outlined text-[16px]">skip_next</span>
                        </button>
                    </div>
                    <div id="status-icons" class="flex gap-2" style="display:none;">
                        <span id="icon-correct" class="material-symbols-outlined text-green-600 text-3xl" data-icon="check_circle" style="display:none;">check_circle</span>
                    </div>
                </div>
                
                <div id="answer-display" class="bg-gray-50 border-2 border-primary/20 rounded-2xl h-20 flex items-center justify-center gap-3 shadow-inner text-3xl font-bold text-primary">
                </div>
            </div>

            <div id="jumbled-letters-grid" class="flex flex-wrap justify-center gap-4 max-w-2xl mx-auto">
            </div>

            <div class="flex flex-col md:flex-row items-center justify-center gap-6 pt-8">
                <button id="next-btn" onclick="fetchQuestion()" class="flex items-center gap-3 bg-orange-500 text-white px-10 py-4 rounded-full tactile-btn-orange font-bold text-xl group" style="display: none;">
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
    let correctLettersArray = []; 
    let currentAnswerArray = [];  
    let clickedButtons = [];      
    let score = 0;
    let questionNumber = 0;       
    let totalChapterQuestions = 0;
    let selectedClass = "";
    let selectedChapter = "";

    function startGame() {
        selectedClass = document.getElementById('class-select').value;
        selectedChapter = document.getElementById('chapter-select').value;
        document.getElementById('quiz-area').style.display = 'block';
        
        // Reset counters
        questionNumber = 0; 
        score = 0;
        document.getElementById('score-display').innerText = "மதிப்பெண்: " + score;
        
        fetchQuestion();
    }

    function fetchQuestion() {
        questionNumber++;
        document.getElementById('next-btn').style.display = 'none';
        document.getElementById('undo-btn').style.display = 'none';
        document.getElementById('skip-btn').style.display = 'flex'; // தவிர் பட்டனை காண்பி
        document.getElementById('answer-display').innerHTML = "";
        document.getElementById('status-icons').style.display = 'none';
        document.getElementById('icon-correct').style.display = 'none';
        
        currentAnswerArray = [];
        clickedButtons = [];
        
        fetch(`/get_question?vakuppu=${encodeURIComponent(selectedClass)}&iyal=${encodeURIComponent(selectedChapter)}`)
            .then(response => response.json())
            .then(data => {
                if(data.error) {
                    document.getElementById('question-text').innerHTML = "⚠️ " + data.error;
                    document.getElementById('sentence-text').innerHTML = "இந்த இயலில் கேள்விகள் இன்னும் சேர்க்கப்படவில்லை.";
                    document.getElementById('jumbled-letters-grid').innerHTML = "";
                    questionNumber--; 
                    return;
                }
                
                totalChapterQuestions = data.total_questions;

                // இயலை வெற்றிகரமாக முடித்துவிட்டால் (Game Over Screen)
                if (questionNumber > totalChapterQuestions) {
                    document.getElementById('quiz-area').innerHTML = `
                        <div class="p-12 text-center space-y-6 bg-surface-container-lowest">
                            <span class="material-symbols-outlined text-6xl text-orange-500">emoji_events</span>
                            <h2 class="text-4xl font-bold text-primary">வாழ்த்துகள்!</h2>
                            <p class="text-2xl text-gray-700">இந்த இயலை வெற்றிகரமாக முடித்துவிட்டீர்கள்.</p>
                            <p class="text-3xl text-primary font-bold mt-4">உங்களின் மொத்த மதிப்பெண்: ${score}</p>
                            <button onclick="location.reload()" class="mt-8 bg-orange-500 text-white px-8 py-3 rounded-xl tactile-btn-orange font-bold text-xl shadow-lg">மீண்டும் விளையாடு</button>
                        </div>
                    `;
                    document.getElementById('remaining-display').style.display = 'none';
                    return;
                }
                
                // மீதமுள்ள கேள்விகளைக் கணக்கிடுதல்
                let remaining = totalChapterQuestions - questionNumber;
                document.getElementById('remaining-display').style.display = 'inline-block';
                document.getElementById('remaining-display').innerText = "மீதம்: " + remaining;

                document.getElementById('question-text').innerHTML = questionNumber + ". " + data.question;
                document.getElementById('sentence-text').innerHTML = data.sentence;
                
                correctLettersArray = data.correct_letters_array; 
                
                let lettersHTML = "";
                let colors = ['bg-primary tactile-btn text-white hover:bg-teal-700', 'bg-orange-500 tactile-btn-orange text-white hover:bg-orange-600'];
                
                data.jumbled_letters.forEach((letter, index) => {
                    let colorClass = colors[index % 2];
                    lettersHTML += `<button class="w-16 h-16 md:w-20 md:h-20 rounded-xl font-bold text-3xl flex items-center justify-center transition-all letter-btn ${colorClass}" onclick="addLetter('${letter}', this)">${letter}</button>`;
                });
                document.getElementById('jumbled-letters-grid').innerHTML = lettersHTML;
            });
    }

    function addLetter(letter, btnElement) {
        let currentIndex = currentAnswerArray.length;
        
        if (letter === correctLettersArray[currentIndex]) {
            currentAnswerArray.push(letter);
            clickedButtons.push(btnElement);
            btnElement.style.display = 'none';
            document.getElementById('undo-btn').style.display = 'flex';
            updateAnswerDisplay();
            
            if (currentAnswerArray.length === correctLettersArray.length) {
                document.getElementById('status-icons').style.display = 'flex';
                document.getElementById('icon-correct').style.display = 'block';
                document.getElementById('next-btn').style.display = 'flex';
                document.getElementById('undo-btn').style.display = 'none'; 
                document.getElementById('skip-btn').style.display = 'none'; // முடித்த பின் தவிர் தேவையில்லை
                
                let audio = document.getElementById('success-sound');
                audio.volume = 0.5; audio.play();
                score += 10;
                document.getElementById('score-display').innerText = "மதிப்பெண்: " + score;
            }
        } else {
            btnElement.classList.add('shake-error');
            let errAudio = document.getElementById('error-sound');
            errAudio.volume = 0.5; errAudio.play();
            
            setTimeout(() => {
                btnElement.classList.remove('shake-error');
            }, 400);
        }
    }

    function undoLetter() {
        if (currentAnswerArray.length === 0) return;
        
        currentAnswerArray.pop(); 
        let btn = clickedButtons.pop(); 
        btn.style.display = 'flex'; 
        
        updateAnswerDisplay();
        
        if (currentAnswerArray.length === 0) {
            document.getElementById('undo-btn').style.display = 'none';
        }
    }

    // தவிர் பட்டன் செயல்பாடு (Skip Logic)
    function skipQuestion() {
        fetchQuestion();
    }

    function updateAnswerDisplay() {
        let html = "";
        currentAnswerArray.forEach(l => {
            html += `<div class="w-12 h-12 bg-white rounded-lg flex items-center justify-center shadow-sm border border-gray-200">${l}</div>`;
        });
        document.getElementById('answer-display').innerHTML = html;
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
        
        filtered_data = []
        for row in data_list:
            if row.get('வகுப்பு', '').strip() == vakuppu and row.get('இயல்', '').strip() == iyal:
                filtered_data.append(row)
                
        if not filtered_data:
             return jsonify({"error": f"{vakuppu} - {iyal} இல் தரவுகள் இல்லை!"})
             
        total_questions_count = len(filtered_data)
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
            letters = ["பி", "ழை"]
            jumbled = ["பி", "ழை"]

        sentence_with_blank = full_answer.replace(word_to_jumble, "<span class='blank'>________</span>")

        return jsonify({
            'question': question,
            'sentence': sentence_with_blank,
            'jumbled_letters': jumbled,
            'correct_word': word_to_jumble,
            'correct_letters_array': letters,
            'total_questions': total_questions_count
        })

if __name__ == '__main__':
    app.run(debug=False)
