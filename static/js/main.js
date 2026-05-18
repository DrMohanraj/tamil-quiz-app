let state = {
  currentIndex: 0,
  score: 0,
  streak: 0
};

let targetWord = "";
let targetLetters = [];
let currentGuess = []; // பயனர் தேர்ந்தெடுக்கும் எழுத்துக்கள்
let isChecking = false;

const elements = {
  questionText: document.getElementById('question-text'),
  answerSlots: document.getElementById('answer-slots'),
  jumbledLetters: document.getElementById('jumbled-letters'),
  streakCounter: document.getElementById('streak-counter'),
  scoreCounter: document.getElementById('score-counter'),
  progressBar: document.getElementById('progress-bar'),
  qCount: document.getElementById('q-count')
};

// தமிழ் எழுத்துக்களைச் சரியாகப் பிரிப்பதற்கான Function (உ-ம்: 'க்', 'கி' பிரியாமல் இருக்க)
function splitTamilWord(word) {
  if (typeof Intl !== 'undefined' && Intl.Segmenter) {
    const segmenter = new Intl.Segmenter('ta', { granularity: 'grapheme' });
    return Array.from(segmenter.segment(word)).map(s => s.segment);
  }
  // பழைய பிரவுசர்களுக்கான மாற்று வழி
  return word.match(/[\u0B80-\u0BFF][\u0BBE-\u0BCD\u0BD7]*|./g) || [];
}

function initQuiz() {
  if (!quizData || quizData.length === 0) {
    elements.questionText.textContent = "கேள்விகள் கிடைக்கவில்லை.";
    return;
  }
  loadQuestion(state.currentIndex);
}

function loadQuestion(index) {
  if (index >= quizData.length) {
    elements.questionText.innerHTML = `🎉 வினாடி வினா முடிந்தது!<br><br>உங்கள் மொத்த மதிப்பெண்: <span style="color:var(--c-gold)">${state.score}</span>`;
    elements.answerSlots.innerHTML = '';
    elements.jumbledLetters.innerHTML = '';
    return;
  }

  isChecking = false;
  const q = quizData[index];
  const question = q['Question'] || q['question'] || q['கேள்வி'];
  const answer = q['Answer'] || q['answer'] || q['விடை'];

  targetWord = answer.trim();
  targetLetters = splitTamilWord(targetWord);
  
  // காலியிடங்களை உருவாக்குதல் (இடைவெளி 'Space' இருந்தால் அதையும் சேர்த்துக்கொள்ளும்)
  currentGuess = targetLetters.map(letter => {
    if (letter.trim() === '') return { letter: ' ', isSpace: true };
    return null;
  });

  elements.questionText.textContent = question;
  elements.qCount.textContent = `கேள்வி ${index + 1}/${quizData.length}`;
  elements.progressBar.style.width = `${((index) / quizData.length) * 100}%`;

  renderSlots();
  
  // எழுத்துக்களைக் கலைத்தல் (Shuffling)
  const playableLetters = targetLetters.filter(l => l.trim() !== '');
  const shuffled = playableLetters.sort(() => Math.random() - 0.5);
  renderLetters(shuffled);
}

// விடைக்கான கட்டங்களை (Slots) வரைதல்
function renderSlots() {
  elements.answerSlots.innerHTML = '';
  
  currentGuess.forEach((slotData, index) => {
    const slot = document.createElement('div');
    slot.className = 'slot';
    
    if (slotData) {
      if (slotData.isSpace) {
        slot.classList.add('space-slot');
      } else {
        slot.textContent = slotData.letter;
        slot.classList.add('filled');
        // கட்டத்தில் உள்ள எழுத்தை மீண்டும் கீழே அனுப்ப
        slot.onclick = () => {
          if(!isChecking) removeLetter(index);
        };
      }
    }
    elements.answerSlots.appendChild(slot);
  });
}

// கலைக்கப்பட்ட எழுத்துக்களைக் கீழே வரைதல்
function renderLetters(letters) {
  elements.jumbledLetters.innerHTML = '';
  
  letters.forEach(letter => {
    const btn = document.createElement('button');
    btn.className = 'letter-btn';
    btn.textContent = letter;
    btn.onclick = () => {
      if(!isChecking) addLetter(letter, btn);
    };
    elements.jumbledLetters.appendChild(btn);
  });
}

// எழுத்தை க்ளிக் செய்தவுடன் மேலேயுள்ள காலியிடத்திற்கு மாற்றுதல்
function addLetter(letter, btnElement) {
  const emptyIndex = currentGuess.findIndex(v => v === null);
  if (emptyIndex !== -1) {
    currentGuess[emptyIndex] = { letter, btnElement };
    btnElement.classList.add('hidden');
    renderSlots();
    checkAnswer();
  }
}

// மேலே உள்ள எழுத்தைக் க்ளிக் செய்தால் மீண்டும் கீழே வருதல்
function removeLetter(index) {
  if (currentGuess[index] && !currentGuess[index].isSpace) {
    currentGuess[index].btnElement.classList.remove('hidden');
    currentGuess[index] = null;
    renderSlots();
  }
}

// விடையைச் சரிபார்த்தல்
function checkAnswer() {
  // அனைத்து கட்டங்களும் நிரம்பிவிட்டனவா என்று பார்த்தல்
  if (currentGuess.every(v => v !== null)) {
    isChecking = true;
    const guessedWord = currentGuess.map(v => v.letter).join('');
    const slots = elements.answerSlots.children;

    if (guessedWord === targetWord) {
      // விடை சரி
      Array.from(slots).forEach(slot => {
        if (!slot.classList.contains('space-slot')) slot.classList.add('correct');
      });
      
      state.streak++;
      state.score += 10 * (1 + (state.streak * 0.1));
      triggerHapticFeedback(true);
      updateMetrics();

      setTimeout(() => {
        state.currentIndex++;
        loadQuestion(state.currentIndex);
      }, 1000);

    } else {
      // விடை தவறு
      Array.from(slots).forEach(slot => {
        if (!slot.classList.contains('space-slot')) slot.classList.add('wrong');
      });
      
      state.streak = 0;
      updateMetrics();
      triggerHapticFeedback(false);

      // 0.8 வினாடிகளுக்குப் பிறகு எழுத்துக்களைத் தானாகவே கீழே அனுப்பிவிடுதல்
      setTimeout(() => {
        currentGuess.forEach((v, i) => {
          if (v && !v.isSpace) {
            v.btnElement.classList.remove('hidden');
            currentGuess[i] = null;
          }
        });
        isChecking = false;
        renderSlots();
      }, 800);
    }
  }
}

function updateMetrics() {
  elements.streakCounter.textContent = state.streak;
  elements.scoreCounter.textContent = Math.round(state.score);
}

function triggerHapticFeedback(isCorrect) {
  if (window.navigator && window.navigator.vibrate) {
    window.navigator.vibrate(isCorrect ? [50] : [100, 50, 100]);
  }
}

initQuiz();
