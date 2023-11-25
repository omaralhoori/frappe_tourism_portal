// Set the countdown time in seconds
var dateObject = new Date(document.getElementById('session-timer').getAttribute("datetime"));
var currentDate = new Date();

// Calculate the difference in milliseconds
var timeDifference = dateObject.getTime() - currentDate.getTime();

const countdownTime = Math.round(Math.max(timeDifference / 1000, 0)); // 5 minutes
console.log(countdownTime)
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

function confirmReservationButtonClicked(e){
  
}