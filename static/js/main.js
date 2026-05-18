let state = {
  currentIndex: 0,
  score: 0,
  streak: 0,
  isAnswered: false
};

const elements = {
  questionText: document.getElementById('question-text'),
  optionsGrid: document.getElementById('options-grid'),
  streakCounter: document.getElementById('streak-counter'),
  scoreCounter: document.getElementById('score-counter'),
  progressBar: document.getElementById('progress-bar'),
  qCount: document.getElementById('q-count')
};

// வினாடி வினாவைத் தொடங்குதல்
function initQuiz() {
  if (!quizData || quizData.length === 0) {
    elements.questionText.textContent = "கேள்விகள் கிடைக்கவில்லை. CSV ஃபைலை சரிபார்க்கவும்.";
    elements.optionsGrid.innerHTML = '';
    return;
  }
  loadQuestion(state.currentIndex);
}

// கேள்வியை திரையில் காட்டுதல்
function loadQuestion(index) {
  if (index >= quizData.length) {
    elements.questionText.innerHTML = `🎉 வினாடி வினா முடிந்தது!<br><br>உங்கள் மொத்த மதிப்பெண்: <span style="color:var(--c-gold)">${state.score}</span>`;
    elements.optionsGrid.innerHTML = '';
    return;
  }

  const q = quizData[index];
  state.isAnswered = false;
  
  // CSV-ல் உள்ள Column பெயர்கள் (உங்கள் CSV-ல் எப்படி உள்ளதோ அதற்கேற்ப எடுத்துக்கொள்ளும்)
  const question = q['Question'] || q['question'] || q['கேள்வி'];
  const opt1 = q['Option1'] || q['option1'] || q['Option 1'];
  const opt2 = q['Option2'] || q['option2'] || q['Option 2'];
  const opt3 = q['Option3'] || q['option3'] || q['Option 3'];
  const opt4 = q['Option4'] || q['option4'] || q['Option 4'];
  const answer = q['Answer'] || q['answer'] || q['விடை'];

  elements.questionText.textContent = question;
  elements.optionsGrid.innerHTML = '';

  // 4 ஆப்ஷன்களை பட்டன்களாக மாற்றுதல்
  const options = [opt1, opt2, opt3, opt4].filter(o => o); // காலியாக உள்ளவற்றை நீக்க

  options.forEach(opt => {
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.textContent = opt;
    btn.onclick = () => handleAnswer(btn, opt, answer);
    elements.optionsGrid.appendChild(btn);
  });

  elements.qCount.textContent = `கேள்வி ${index + 1}/${quizData.length}`;
  elements.progressBar.style.width = `${((index) / quizData.length) * 100}%`;
}

// விடையை சரிபார்த்தல்
function handleAnswer(btn, selected, correct) {
  if (state.isAnswered) return;
  state.isAnswered = true;

  // விடை சரி என்றால்
  if (selected.trim() === correct.trim()) {
    btn.classList.add('correct');
    state.streak++;
    const points = 10 * (1 + (state.streak * 0.1)); // தொடர்ந்து சரியாகச் சொன்னால் போனஸ்
    state.score += Math.round(points);
    triggerHapticFeedback(true);
  } 
  // விடை தவறு என்றால்
  else {
    btn.classList.add('wrong');
    state.streak = 0;
    
    // சரியான விடையைக் காண்பித்தல்
    Array.from(elements.optionsGrid.children).forEach(b => {
      if (b.textContent.trim() === correct.trim()) {
        b.classList.add('correct');
      }
    });
    triggerHapticFeedback(false);
  }

  updateMetrics();

  // 1.5 வினாடிகளுக்குப் பிறகு அடுத்த கேள்விக்குச் செல்லுதல்
  setTimeout(() => {
    state.currentIndex++;
    loadQuestion(state.currentIndex);
  }, 1500);
}

function updateMetrics() {
  elements.streakCounter.textContent = state.streak;
  elements.scoreCounter.textContent = state.score;
  
  elements.scoreCounter.parentElement.style.transform = 'scale(1.1)';
  setTimeout(() => elements.scoreCounter.parentElement.style.transform = 'scale(1)', 200);
}

function triggerHapticFeedback(isCorrect) {
  if (window.navigator && window.navigator.vibrate) {
    window.navigator.vibrate(isCorrect ? [50] : [100, 50, 100]);
  }
}

// ஆப் தொடக்கம்
initQuiz();
