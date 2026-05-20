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

# --- NEW GAMIFIED UI (DUOLINGO/WORDWALL STYLE) ---
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
        /* கொற்கை எழுத்துரு */
        @font-face {
            font-family: 'Korkai';
            src: url("{{ url_for('static', filename='fonts/Korkai-Black.ttf') }}") format('truetype');
            font-weight: 900;
        }

        body {
            font-family: 'Korkai', sans-serif;
            background: linear-gradient(135deg, #eef2ff 0%, #f3e8ff 100%);
            min-height: 100vh;
        }

        .material-symbols-outlined { 
            font-family: 'Material Symbols Outlined' !important; 
            font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24; 
        }

        /* 3D Gamified Buttons */
        .btn-3d-primary {
            background-color: #6366f1; /* Indigo */
            color: white;
            box-shadow: 0 6px 0 #4338ca;
            transition: all 0.1s;
        }
        .btn-3d-primary:active {
            transform: translateY(6px);
            box-shadow: 0 0px 0 #4338ca;
        }

        .btn-3d-secondary {
            background-color: #ec4899; /* Pink */
            color: white;
            box-shadow: 0 6px 0 #be185d;
            transition: all 0.1s;
        }
        .btn-3d-secondary:active {
            transform: translateY(6px);
            box-shadow: 0 0px 0 #be185d;
        }

        .btn-3d-letter {
            background-color: #ffffff;
            color: #4f46e5;
            box-shadow: 0 6px 0 #c7d2fe;
            border: 2px solid #e0e7ff;
            transition: all 0.1s;
        }
        .btn-3d-letter:hover {
            background-color: #e0e7ff;
        }
        .btn-3d-letter:active {
            transform: translateY(6px);
            box-shadow: 0 0px 0 #c7d2fe;
        }

        /* White Card with soft shadow */
        .game-card {
            background: white;
            border-radius: 24px;
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.1);
            border: 4px solid white;
        }

        .blank { color: #ec4899; font-weight: bold; text-decoration: underline; }
        
        /* Progress Bar Animation */
        .progress-fill {
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* Shake Error */
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
    </style>
</head>
<body class="text-gray-800">

<header class="flex justify-between items-center w-full px-6 py-4 sticky top-0 z-50 bg-white/70 backdrop-blur-md border-b-2 border-indigo-100">
    <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-3xl text-indigo-500">menu_book</span>
        <h1 class="text-2xl font-extrabold text-indigo-900 tracking-wide">சொல்-களஞ்சியம்</h1>
    </div>
    <div class="flex items-center gap-4">
        <div class="bg-indigo-100 px-4 py-2 rounded-2xl flex items-center gap-2 border-2 border-indigo-200">
            <span class="material-symbols-outlined text-indigo-600">stars</span>
            <span id="score-display" class="font-bold text-indigo-800 text-lg">0</span>
        </div>
    </div>
</header>

<main class="max-w-[900px] mx-auto px-4 py-8 space-y-8">
    
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

    <section id="quiz-area" class="game-card p-6 md:p-10" style="display: none;">
        
        <div class="w-full bg-gray-200 rounded-full h-4 mb-8 border-2 border-gray-300 overflow-hidden relative">
            <div id="progress-bar" class="bg-gradient-to-r from-pink-400 to-pink-600 h-full rounded-full progress-fill" style="width: 0%;"></div>
        </div>

        <div class="flex items-center justify-between mb-6">
            <h2 id="question-text" class="text-2xl font-bold text-indigo-900 bg-indigo-50 px-4 py-2 rounded-xl border border-indigo-100 inline-block">
                கேள்வி...
            </h2>
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

            <div id="answer-display" class="flex flex-wrap items-center justify-center gap-3 min-h-[80px]">
                </div>

            <div id="jumbled-letters-grid" class="flex flex-wrap justify-center gap-4 mt-8 bg-indigo-50 p-6 rounded-3xl border-2 border-indigo-100">
                </div>
            
            <div id="status-message" class="hidden justify-center items-center gap-2 mt-4">
                <span class="material-symbols-outlined text-4xl text-green-500 animate-bounce">check_circle</span>
                <span class="text-2xl font-bold text-green-600">சரியான விடை!</span>
            </div>

            <button id="next-btn" onclick="fetchQuestion()" class="mx-auto mt-8 px-12 py-4 rounded-2xl btn-3d-secondary text-xl font-bold tracking-wider" style="display: none;">
                அடுத்தது <span class="material-symbols-outlined align-middle ml-1">arrow_forward</span>
            </button>
        </div>
    </section>

</main>

<audio id="success-sound" src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3"></audio>
<audio id="error-sound" src="https://assets.mixkit.co/active_storage/sfx/2954/2954-preview.mp3"></audio>
<audio id="win-sound" src="https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3"></audio>

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
        
        document.getElementById('setup-area').style.display = 'none';
        document.getElementById('quiz-area').style.display = 'block';
        
        questionNumber = 0; 
        score = 0;
        document.getElementById('score-display').innerText = score;
        
        fetchQuestion();
    }

    function fetchQuestion() {
        questionNumber++;
        document.getElementById('next-btn').style.display = 'none';
        document.getElementById('undo-btn').style.display = 'none';
        document.getElementById('skip-btn').style.display = 'block'; 
        document.getElementById('status-message').style.display = 'none';
        
        currentAnswerArray = [];
        clickedButtons = [];
        
        fetch(`/get_question?vakuppu=${encodeURIComponent(selectedClass)}&iyal=${encodeURIComponent(selectedChapter)}`)
            .then(response => response.json())
            .then(data => {
                if(data.error) {
                    document.getElementById('question-text').innerHTML = "⚠️ பிழை";
                    document.getElementById('sentence-text').innerHTML = data.error;
                    document.getElementById('jumbled-letters-grid').innerHTML = "";
                    document.getElementById('skip-btn').style.display = 'none';
                    questionNumber--; 
                    return;
                }
                
                totalChapterQuestions = data.total_questions;

                // Update Progress Bar
                let progressPercentage = ((questionNumber - 1) / totalChapterQuestions) * 100;
                document.getElementById('progress-bar').style.width = progressPercentage + '%';

                // Game Over Screen
                if (questionNumber > totalChapterQuestions) {
                    document.getElementById('progress-bar').style.width = '100%';
                    document.getElementById('win-sound').play();
                    
                    document.getElementById('quiz-area').innerHTML = `
                        <div class="text-center space-y-6 py-10">
                            <span class="material-symbols-outlined text-8xl text-yellow-400 drop-shadow-lg">trophy</span>
                            <h2 class="text-4xl font-extrabold text-indigo-900">அற்புதம்!</h2>
                            <p class="text-xl text-gray-600 font-bold">இந்த இயலை வெற்றிகரமாக முடித்துவிட்டீர்கள்.</p>
                            <div class="bg-indigo-100 inline-block px-8 py-4 rounded-3xl border-4 border-indigo-200 mt-6">
                                <p class="text-lg text-indigo-800 font-bold">மொத்த மதிப்பெண்</p>
                                <p class="text-6xl text-indigo-600 font-extrabold mt-2">${score}</p>
                            </div>
                            <br>
                            <button onclick="location.reload()" class="mt-10 px-12 py-4 rounded-2xl btn-3d-primary text-xl font-bold tracking-wider">
                                முகப்புக்குச் செல்
                            </button>
                        </div>
                    `;
                    return;
                }
                
                document.getElementById('question-text').innerHTML = questionNumber + ". " + data.question;
                document.getElementById('sentence-text').innerHTML = data.sentence;
                
                correctLettersArray = data.correct_letters_array; 
                
                // Create empty slots for the answer
                let slotsHTML = "";
                for(let i=0; i<correctLettersArray.length; i++){
                    slotsHTML += `<div class="w-14 h-14 md:w-16 md:h-16 bg-gray-100 rounded-2xl border-4 border-dashed border-gray-300 flex items-center justify-center text-3xl font-bold text-indigo-700"></div>`;
                }
                document.getElementById('answer-display').innerHTML = slotsHTML;

                let lettersHTML = "";
                data.jumbled_letters.forEach((letter, index) => {
                    lettersHTML += `<button class="w-16 h-16 md:w-20 md:h-20 rounded-2xl font-bold text-3xl flex items-center justify-center btn-3d-letter" onclick="addLetter('${letter}', this)">${letter}</button>`;
                });
                document.getElementById('jumbled-letters-grid').innerHTML = lettersHTML;
            });
    }

    function addLetter(letter, btnElement) {
        let currentIndex = currentAnswerArray.length;
        
        if (letter === correctLettersArray[currentIndex]) {
            currentAnswerArray.push(letter);
            clickedButtons.push(btnElement);
            btnElement.style.visibility = 'hidden'; // Hide but keep space
            document.getElementById('undo-btn').style.display = 'block';
            updateAnswerDisplay();
            
            if (currentAnswerArray.length === correctLettersArray.length) {
                document.getElementById('status-message').style.display = 'flex';
                document.getElementById('next-btn').style.display = 'block';
                document.getElementById('undo-btn').style.display = 'none'; 
                document.getElementById('skip-btn').style.display = 'none'; 
                
                let audio = document.getElementById('success-sound');
                audio.volume = 0.5; audio.play();
                score += 10;
                document.getElementById('score-display').innerText = score;
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
        btn.style.visibility = 'visible'; 
        
        updateAnswerDisplay();
        
        if (currentAnswerArray.length === 0) {
            document.getElementById('undo-btn').style.display = 'none';
        }
    }

    function skipQuestion() {
        fetchQuestion();
    }

    function updateAnswerDisplay() {
        let slots = document.getElementById('answer-display').children;
        for(let i=0; i<correctLettersArray.length; i++){
            if(i < currentAnswerArray.length) {
                slots[i].innerHTML = currentAnswerArray[i];
                slots[i].className = "w-14 h-14 md:w-16 md:h-16 bg-white rounded-2xl border-4 border-indigo-400 flex items-center justify-center text-3xl font-bold text-indigo-700 shadow-md transform scale-110 transition-transform";
            } else {
                slots[i].innerHTML = "";
                slots[i].className = "w-14 h-14 md:w-16 md:h-16 bg-gray-100 rounded-2xl border-4 border-dashed border-gray-300 flex items-center justify-center text-3xl font-bold text-indigo-700";
            }
        }
    }
</script>
</body>
</html>
"""

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

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
