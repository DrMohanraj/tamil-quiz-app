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
        <div class="flex flex-col md:flex-row justify-between items-center gap-4">
            <div class="flex flex-col w-full md:w-auto">
                <span class="text-xs text-outline mb-1">வகுப்பைத் தேர்ந்தெடு</span>
                <select id="class-select" class="text-lg font-bold text-on-surface bg-surface-container-low border border-outline-variant rounded-lg px-2 py-1 outline-none cursor-pointer">
                    <option value="6-ஆம் வகுப்பு">6-ஆம் வகுப்பு</option>
                    <option value="7-ஆம் வகுப்பு">7-ஆம் வகுப்பு</option>
                    <option value="8-ஆம் வகுப்பு">8-ஆம் வகுப்பு</option>
                    <option value="9-ஆம் வகுப்பு">9-ஆம் வகுப்பு</option>
                </select>
            </div>
            <div class="flex flex-col w-full md:w-auto">
                <span class="text-xs text-outline mb-1">இயலைத் தேர்ந்தெடு</span>
                <select id="chapter-select" class="text-lg font-bold text-on-surface bg-surface-container-low border border-outline-variant rounded-lg px-2 py-1 outline-none cursor-pointer">
                    <option value="இயல் 1">இயல் 1</option>
                    <option value="இயல் 2">இயல் 2</option>
                    <option value="இயல் 3">இயல் 3</option>
                </select>
            </div>
            <button onclick="startGame()" class="w-full md:w-auto bg-primary text-on-primary px-6 py-3 rounded-lg font-bold active:scale-95 transition-transform shadow-md">
                விளையாடத் தொடங்கு
            </button>
        </div>
    </section>

    <section id="quiz-area" class="flex flex-col gap-md" style="display:none;">
        
        <div class="bento-card bg-surface-container-lowest p-lg rounded-xl border-t-4 border-primary relative">
            <div class="flex justify-between items-center mb-2">
                <span id="question-indicator" class="text-sm font-bold text-primary uppercase">கேள்வி ஏற்றப்படுகிறது...</span>
                <button onclick="skipQuestion()" class="text-xs bg-surface-variant text-on-surface-variant px-3 py-1 rounded-full hover:bg-outline-variant flex items-center gap-1 active:scale-95">
                    தவிர் <span class="material-symbols-outlined text-[14px]">skip_next</span>
                </button>
            </div>
            <p id="sentence-text" class="text-2xl text-on-surface leading-snug font-bold"></p>
        </div>

        <div class="flex flex-col items-center gap-xs mt-4">
            <span class="text-sm text-outline-variant font-bold">உன் விடை:</span>
            <div id="answer-display" class="flex flex-wrap justify-center gap-xs min-h-[60px]">
            </div>
        </div>

        <div id="status-message" class="hidden justify-center items-center gap-2 mt-2">
            <span class="material-symbols-outlined text-3xl text-tertiary animate-bounce">check_circle</span>
            <span class="text-xl font-bold text-tertiary">சரியான விடை!</span>
        </div>

        <div id="jumbled-letters-grid" class="grid grid-cols-3 gap-md mt-4">
        </div>

        <button id="next-btn" onclick="fetchQuestion()" style="display:none;" class="mt-lg w-full bg-primary h-14 rounded-xl flex items-center justify-center gap-md text-on-primary font-bold text-xl shadow-lg active:scale-95 transition-transform duration-200">
            அடுத்த கேள்வி <span class="material-symbols-outlined">arrow_forward</span>
        </button>
    </section>

    <section id="stats-area" class="flex flex-wrap justify-center gap-sm mt-md" style="display:none;">
        <div class="flex items-center gap-xs px-3 py-2 bg-surface-variant rounded-full text-on-surface-variant text-sm font-bold">
            <span class="material-symbols-outlined text-[18px]">lightbulb</span> உதவி
        </div>
        <div id="progress-chip" class="flex items-center gap-xs px-3 py-2 bg-secondary-container rounded-full text-on-secondary-container text-sm font-bold shadow-sm">
            <span class="material-symbols-outlined text-[18px]">flag</span> 1 / 10
        </div>
    </section>

    <div id="hero-image" class="mt-lg mb-8 rounded-2xl overflow-hidden aspect-[21/9] relative shadow-md">
        <div class="absolute inset-0 bg-gradient-to-r from-primary/20 to-secondary/20 mix-blend-multiply"></div>
        <img class="w-full h-full object-cover grayscale-[20%]" src="https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&q=80&w=800"/>
    </div>

</main>

<nav class="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-2 py-2 pb-safe bg-surface-container-low border-t border-outline-variant shadow-lg rounded-t-xl">
    <a class="flex flex-col items-center justify-center text-on-surface-variant px-3 py-1 hover:bg-surface-container-highest transition-colors active:scale-90 duration-150 rounded-lg" href="#">
        <span class="material-symbols-outlined">home</span><span class="text-xs font-bold mt-1">Home</span>
    </a>
    <a class="flex flex-col items-center justify-center text-on-surface-variant px-3 py-1 hover:bg-surface-container-highest transition-colors active:scale-90 duration-150 rounded-lg" href="#">
        <span class="material-symbols-outlined">menu_book</span><span class="text-xs font-bold mt-1">Lessons</span>
    </a>
    <a class="flex flex-col items-center justify-center bg-secondary-container text-on-secondary-container rounded-xl px-4 py-2 active:scale-90 transition-transform duration-150 shadow-md" href="#">
        <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">extension</span><span class="text-xs font-bold mt-1">Games</span>
    </a>
    <a class="flex flex-col items-center justify-center text-on-surface-variant px-3 py-1 hover:bg-surface-container-highest transition-colors active:scale-90 duration-150 rounded-lg" href="#">
        <span class="material-symbols-outlined">person</span><span class="text-xs font-bold mt-1">Profile</span>
    </a>
</nav>

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
        document.getElementById('hero-image').style.display = 'none';
        document.getElementById('quiz-area').style.display = 'flex';
        document.getElementById('stats-area').style.display = 'flex';
        
        questionNumber = 0; 
        score = 0;
        document.getElementById('score-display').innerText = score;
        
        fetchQuestion();
    }

    function fetchQuestion() {
        questionNumber++;
        document.getElementById('next-btn').style.display = 'none';
        document.getElementById('status-message').style.display = 'none';
        currentAnswerArray = [];
        clickedButtons = [];
        
        fetch(`/get_question?vakuppu=${encodeURIComponent(selectedClass)}&iyal=${encodeURIComponent(selectedChapter)}`)
            .then(response => response.json())
            .then(data => {
                if(data.error) {
                    document.getElementById('question-indicator').innerHTML = "⚠️ பிழை";
                    document.getElementById('sentence-text').innerHTML = data.error;
                    document.getElementById('jumbled-letters-grid').innerHTML = "";
                    questionNumber--; 
                    return;
                }
                
                totalChapterQuestions = data.total_questions;
                document.getElementById('progress-chip').innerHTML = `<span class="material-symbols-outlined text-[18px]">flag</span> ${questionNumber} / ${totalChapterQuestions}`;

                if (questionNumber > totalChapterQuestions) {
                    document.getElementById('win-sound').play();
                    document.getElementById('quiz-area').innerHTML = `
                        <div class="bento-card bg-surface-container-lowest p-10 rounded-xl border-t-4 border-tertiary text-center space-y-6">
                            <span class="material-symbols-outlined text-6xl text-secondary">emoji_events</span>
                            <h2 class="text-3xl font-extrabold text-on-surface">அற்புதம்!</h2>
                            <p class="text-lg text-on-surface-variant font-bold">இந்த இயலை வெற்றிகரமாக முடித்துவிட்டீர்கள்.</p>
                            <div class="bg-surface-container-high inline-block px-8 py-4 rounded-2xl mt-4">
                                <p class="text-sm text-on-surface-variant font-bold mb-1">மொத்த மதிப்பெண்</p>
                                <p class="text-5xl text-primary font-extrabold">${score}</p>
                            </div>
                            <button onclick="location.reload()" class="mt-8 w-full bg-primary h-14 rounded-xl flex items-center justify-center text-on-primary font-bold text-xl shadow-lg active:scale-95">முகப்புக்குச் செல்</button>
                        </div>
                    `;
                    return;
                }
                
                document.getElementById('question-indicator').innerHTML = `கேள்வி ${questionNumber}:`;
                document.getElementById('sentence-text').innerHTML = data.sentence;
                correctLettersArray = data.correct_letters_array; 
                
                updateAnswerDisplay();

                let lettersHTML = "";
                const colors = [
                    'bg-primary-container text-on-primary-container',
                    'bg-secondary text-on-secondary',
                    'bg-tertiary text-on-tertiary',
                    'bg-tertiary-container text-on-tertiary-container',
                    'bg-secondary-fixed-dim text-on-secondary-fixed-variant'
                ];
                
                data.jumbled_letters.forEach((letter, index) => {
                    let colorClass = colors[index % colors.length];
                    lettersHTML += `<button class="letter-glow h-20 ${colorClass} rounded-xl flex items-center justify-center text-3xl font-bold shadow-md" onclick="addLetter('${letter}', this)">${letter}</button>`;
                });
                
                lettersHTML += `
                <button id="undo-btn" onclick="undoLetter()" class="letter-glow h-20 bg-surface-container-highest border-2 border-dashed border-outline-variant rounded-xl flex items-center justify-center text-outline-variant opacity-50" disabled>
                    <span class="material-symbols-outlined text-3xl" data-icon="backspace">backspace</span>
                </button>`;
                
                document.getElementById('jumbled-letters-grid').innerHTML = lettersHTML;
            });
    }

    function addLetter(letter, btnElement) {
        let currentIndex = currentAnswerArray.length;
        if (letter === correctLettersArray[currentIndex]) {
            currentAnswerArray.push(letter);
            clickedButtons.push(btnElement);
            btnElement.style.visibility = 'hidden'; 
            
            let undoBtn = document.getElementById('undo-btn');
            if(undoBtn) {
                undoBtn.classList.remove('opacity-50');
                undoBtn.classList.add('text-primary');
                undoBtn.disabled = false;
            }

            updateAnswerDisplay();
            
            if (currentAnswerArray.length === correctLettersArray.length) {
                document.getElementById('status-message').style.display = 'flex';
                document.getElementById('next-btn').style.display = 'flex';
                if(undoBtn) undoBtn.style.display = 'none'; 
                
                let audio = document.getElementById('success-sound');
                audio.volume = 0.5; audio.play();
                score += 10;
                document.getElementById('score-display').innerText = score;
            }
        } else {
            btnElement.classList.add('shake-error');
            let errAudio = document.getElementById('error-sound');
            errAudio.volume = 0.5; errAudio.play();
            setTimeout(() => { btnElement.classList.remove('shake-error'); }, 400);
        }
    }

    function undoLetter() {
        if (currentAnswerArray.length === 0) return;
        currentAnswerArray.pop(); 
        let btn = clickedButtons.pop(); 
        btn.style.visibility = 'visible'; 
        updateAnswerDisplay();
        
        if (currentAnswerArray.length === 0) {
            let undoBtn = document.getElementById('undo-btn');
            undoBtn.classList.add('opacity-50');
            undoBtn.classList.remove('text-primary');
            undoBtn.disabled = true;
        }
    }

    function skipQuestion() { fetchQuestion(); }

    function updateAnswerDisplay() {
        let slotsHTML = "";
        for(let i=0; i<correctLettersArray.length; i++){
            if(i < currentAnswerArray.length) {
                slotsHTML += `<div class="w-12 h-14 bg-surface-container-lowest rounded-lg flex items-center justify-center text-3xl font-bold text-primary shadow-md border-2 border-primary transform scale-105 transition-all">${currentAnswerArray[i]}</div>`;
            } else {
                slotsHTML += `<div class="w-12 h-14 bg-surface-container-high rounded-lg flex items-center justify-center text-3xl font-bold text-primary shadow-inner border border-outline-variant opacity-50"></div>`;
            }
        }
        document.getElementById('answer-display').innerHTML = slotsHTML;
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
