// Set the countdown time in seconds
const countdownTime = 100; // 5 minutes

let timeRemaining = countdownTime;
let timerInterval;

function startTimer() {
  timerInterval = setInterval(updateTimer, 1000);
}

function updateTimer() {
  const hours = Math.floor(timeRemaining / 3600);
  const minutes = Math.floor((timeRemaining % 3600) / 60);
  const seconds = timeRemaining % 60;

  const formattedTime = `${formatTime(hours)}:${formatTime(minutes)}:${formatTime(seconds)}`;
  document.getElementById('session-timer').textContent = formattedTime;

  if (timeRemaining === 0) {
    clearInterval(timerInterval);
   alert('Time is up!');
  } else {
    timeRemaining--;
  }
}

function formatTime(time) {
  return time < 10 ? `0${time}` : time;
}

// Start the timer when the page loads
startTimer();