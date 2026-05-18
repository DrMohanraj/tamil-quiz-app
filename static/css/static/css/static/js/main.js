/**
 * Modern Quiz State Management
 * Connect this to your Flask Backend (tamil_quiz_data.csv) via Fetch API or Jinja templates.
 */

// Example Data Structure (You will feed this from your backend)
const mockData = [
  { sentence: "தமிழ் மொழி ___ சிறப்பு மிக்கது.", options: ["இலக்கியத்தால்", "அளவால்", "எண்ணிக்கையால்", "பணத்தால்"], answer: "இலக்கியத்தால்" },
  { sentence: "மழை ___ பெய்கிறது.", options: ["சத்தமாக", "மெதுவாக", "கொட்டோகொட்டென", "அழகாக"], answer: "கொட்டோகொட்டென" }
];

let state = {
  currentIndex: 0,
  score: 0,
  streak: 0,
  isAnswered: false
};

// DOM Elements
const elements = {
  questionText: document.getElementById('question-text'),
  optionsGrid: document.getElementById('options-grid'),
  streakCounter: document.getElementById('streak-counter'),
  scoreCounter: document.getElementById('score-counter'),
  progressBar: document.getElementById('progress-bar'),
  qCount: document.getElementById('q-count')
};

// Initialize App
function initQuiz() {
  loadQuestion(state.currentIndex);
  updateMetrics();
}

// Load Question
function loadQuestion(index) {
  if (index >= mockData.length) {
    // Redirect to success page or show summary component
    return;
  }

  const q = mockData[index];
  state.isAnswered = false;
  
  // Parse sentence for blank
  const parts = q.sentence.split('___');
  elements.questionText.innerHTML = `${parts[0]} <span class="blank-space" id="blank-space">___</span> ${parts[1] || ''}`;

  // Render Options
  elements.optionsGrid.innerHTML = '';
  // Shuffle options in production
  q.options.forEach(opt => {
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.textContent = opt;
    btn.onclick = () => handleAnswer(btn, opt, q.answer);
    elements.optionsGrid.appendChild(btn);
  });

  // Update Progress
  elements.qCount.textContent = `கேள்வி ${index + 1}/${mockData.length}`;
  elements.progressBar.style.width = `${((index) / mockData.length) * 100}%`;
}

// Handle Answer Logic
function handleAnswer(btn, selected, correct) {
  if (state.isAnswered) return;
  state.isAnswered = true;

  const blank = document.getElementById('blank-space');
  blank.textContent = selected;
  blank.classList.add('filled');

  if (selected === correct) {
    // Correct Answer
    btn.classList.add('correct');
    blank.classList.add('correct');
    
    state.streak++;
    const points = 10 * (1 + (state.streak * 0.1)); // Combo multiplier
    state.score += Math.round(points);
    
    triggerHapticFeedback(true); // For mobile
  } else {
    // Wrong Answer
    btn.classList.add('wrong');
    blank.classList.add('wrong');
    state.streak = 0;
    
    // Highlight correct answer
    Array.from(elements.optionsGrid.children).forEach(b => {
      if (b.textContent === correct) b.classList.add('correct');
    });

    triggerHapticFeedback(false);
  }

  updateMetrics();

  // Move to next question after delay
  setTimeout(() => {
    state.currentIndex++;
    loadQuestion(state.currentIndex);
  }, 1500);
}

function updateMetrics() {
  elements.streakCounter.textContent = state.streak;
  elements.scoreCounter.textContent = state.score;
  
  // Add animation class
  elements.scoreCounter.parentElement.style.transform = 'scale(1.1)';
  setTimeout(() => elements.scoreCounter.parentElement.style.transform = 'scale(1)', 200);
}

// Accessibility & Mobile enhancements
function triggerHapticFeedback(isCorrect) {
  if (window.navigator && window.navigator.vibrate) {
    window.navigator.vibrate(isCorrect ? [50] : [100, 50, 100]);
  }
}

// Start
initQuiz();
