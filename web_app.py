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
<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="UTF-8">
    <title>சொல்-களஞ்சியம்</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #e0f2f1; text-align: center; padding: 30px; }
        .card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); max-width: 700px; margin: auto; border-top: 8px solid #009688; }
        h2 { color: #00796b; margin-bottom: 30px; font-size: 28px;}
        .question { font-size: 22px; color: #333; margin-bottom: 15px; font-weight: bold;}
        .sentence { font-size: 20px; color: #555; margin-bottom: 30px; line-height: 1.5; }
        .letters-container { margin-top: 20px; min-height: 60px; }
        .letter-btn { background-color: #ff9800; color: white; border: none; padding: 15px 25px; font-size: 26px; margin: 8px; border-radius: 12px; cursor: pointer; box-shadow: 0 5px #e68a00; transition: 0.2s; font-weight: bold;}
        .letter-btn:active { box-shadow: 0 0 #e68a00; transform: translateY(5px); }
        .answer-box { font-size: 28px; font-weight: bold; color: #00796b; margin-top: 20px; min-height: 40px; padding: 10px; border-radius: 10px; background-color: #e0f2f1; display: inline-block; min-width: 200px; }
        .next-btn { background-color: #4CAF50; color: white; padding: 12px 25px; font-size: 20px; border: none; border-radius: 8px; cursor: pointer; margin-top: 30px; display: none; box-shadow: 0 4px #388E3C; }
        .next-btn:active { box-shadow: 0 0 #388E3C; transform: translateY(4px); }
        .blank { color: #ff5722; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>📚 சொல்-களஞ்சியம் வினாடி-வினா</h2>
        <div id="question" class="question">கேள்வி ஏற்றப்படுகிறது...</div>
        <div id="sentence" class="sentence"></div>
        
        <div id="answer-area" class="answer-box">விடையைச் சேர்க்கவும்</div><br>
        <div id="letters-area" class="letters-container"></div>
        
        <button id="next-btn" class="next-btn" onclick="fetchQuestion()">அடுத்த கேள்வி ➔</button>
    </div>

    <script>
        let currentCorrectWord = "";
        let currentAnswer = "";

        function fetchQuestion() {
            document.getElementById('next-btn').style.display = 'none';
            document.getElementById('answer-area').innerHTML = "";
            document.getElementById('answer-area').style.color = "#00796b";
            currentAnswer = "";
            
            fetch('/get_question')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('question').innerHTML = "❓ " + data.question;
                    document.getElementById('sentence').innerHTML = data.sentence;
                    currentCorrectWord = data.correct_word;
                    
                    let lettersHTML = "";
                    data.jumbled_letters.forEach(letter => {
                        lettersHTML += `<button class="letter-btn" onclick="addLetter('${letter}', this)">${letter}</button>`;
                    });
                    document.getElementById('letters-area').innerHTML = lettersHTML;
                });
        }

        function addLetter(letter, btnElement) {
            currentAnswer += letter;
            document.getElementById('answer-area').innerHTML = currentAnswer;
            btnElement.style.display = 'none'; 
            
            if (currentAnswer.length === currentCorrectWord.length) {
                if (currentAnswer === currentCorrectWord) {
                    document.getElementById('answer-area').innerHTML += " ✅ சிறப்பு!";
                    document.getElementById('answer-area').style.color = "green";
                    document.getElementById('next-btn').style.display = 'inline-block';
                } else {
                    document.getElementById('answer-area').innerHTML += " ❌ தவறு";
                    document.getElementById('answer-area').style.color = "red";
                    setTimeout(() => {
                        document.getElementById('answer-area').innerHTML = "";
                        currentAnswer = "";
                        let buttons = document.querySelectorAll('.letter-btn');
                        buttons.forEach(btn => btn.style.display = 'inline-block');
                    }, 1500);
                }
            }
        }

        window.onload = fetchQuestion; 
    </script>
</body>
</html>
"""

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# 3. பைதான் மற்றும் இணையதளத்தை இணைக்கும் Flask Server
app = Flask(__name__)
csv_file = "tamil_quiz_data.csv"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_question')
def get_question():
    if not os.path.exists(csv_file):
        return jsonify({"question": "Error: CSV பைல் இல்லை!", "sentence": "", "jumbled_letters": [], "correct_word": ""})
        
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        data_list = list(csv_reader)
        if not data_list:
             return jsonify({"question": "Error: தரவு இல்லை!", "sentence": "", "jumbled_letters": [], "correct_word": ""})
             
        random_row = random.choice(data_list)
        
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

        sentence_with_blank = full_answer.replace(word_to_jumble, "<span class='blank'> ________ </span>")

        return jsonify({
            'question': question,
            'sentence': sentence_with_blank,
            'jumbled_letters': jumbled,
            'correct_word': word_to_jumble
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 உங்களுடைய இணையதளம் வெற்றிகரமாகத் தயாராகிவிட்டது!")
    print("🌐 கீழே உள்ள லிங்க்கை காப்பி செய்து Google Chrome-ல் பேஸ்ட் செய்யவும்:")
    print("👉 http://127.0.0.1:5000 👈")
    print("="*60 + "\n")
    app.run(debug=False)
