var sessionTimer = document.getElementById('session-timer')
if (sessionTimer){
// Set the countdown time in seconds
var dateObject = new Date(sessionTimer.getAttribute("datetime"));
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
}


function confirmReservationButtonClicked(e){
  var rooms = document.querySelectorAll(".hotel_room_container")
  var customerName = document.querySelector('input[name="customer-name"]').value
  var customerEmail = document.querySelector('input[name="email"]').value
  var customerMobile = document.querySelector('input[name="phone-number"]').value
  roomsInfo = {}
  for (var room of rooms){
    var paxes = room.querySelectorAll(".pax-container");
    roomsInfo[room.getAttribute('row-id')] = {}
    for (var pax of paxes){
      var salutInput = pax.querySelector('select[name="pax-salut"]');
      var salut = ""
      if (salutInput){
        // ToDo show Error if empty
        salut = salutInput.value
      }
      roomsInfo[room.getAttribute('row-id')][pax.getAttribute('row-id')] = {
        "salut": salut,
        "guest_name": pax.querySelector('input[name="pax-name"]').value,
        "row_id": pax.getAttribute("row-id")
      }
    }
    var extras = room.querySelectorAll(".extra-price-input:checked")
    roomsInfo[room.getAttribute('row-id')]['extras'] = []
    for (var extra of extras){
      //  ToDo make extra for amount and percentage
      roomsInfo[room.getAttribute('row-id')]['extras'].push({
        "extra": extra.value,
        "extra_price": extra.getAttribute('extra-price'),
        "room_name": extra.getAttribute('room-name')
      })
    }
  }
  var searchParams = new URLSearchParams(window.location.search)
  var invoice = searchParams.get("invoice")
  console.log(invoice)
  frappe.call({
    method: "tourism_portal.api.reserve.complete_reservation",
    args: {
      sales_invoice: invoice,
      rooms: roomsInfo,
      customer_name: customerName,
      customer_email: customerEmail,
      customer_mobile_no: customerMobile
    },
    callback: (res) =>{
      if(res.message && res.message.success_key){
        window.location.reload()
      }else{
        msgprint(res.message.message)
      }
    }
  })
}

function roomExtraChanged(e){
  var extraPrice = e.getAttribute("extra-price");

  if(e.checked){
    changeTotalFees("hotel_fees", extraPrice)
  }else{
    changeTotalFees("hotel_fees", -extraPrice)
  }
}

function changeTotalFees(totalId, amount){
  var totalAmount = Number( document.querySelector(`#${totalId}`).innerText);
  document.querySelector(`#${totalId}`).innerText = totalAmount + Number(amount)
  updateGrandTotal()
}

function updateGrandTotal(){
  var hotelFees = Number(document.querySelector('#hotel_fees').innerText)
  document.querySelector('#total_fees').innerText = hotelFees 
}

function cancelReservation(e){
  var invoiceId = e.getAttribute('invoice-id');
  frappe.confirm("Are you sure you want to cancel the invoice?", ()=> confirmCancelReservation(invoiceId))
}

function confirmCancelReservation(invoiceId){
  frappe.call({
    method: "tourism_portal.api.reserve.cancel_reservation",
    args: {
      invoice_id: invoiceId
    },
    callback: (res) => {
      if(res.message && res.message['success_key']){
        window.location.reload()
      }else if (res.message){
        msgprint(res.message.message)
      }else{
        msgprint("Something went wrong")
      }
    }
  })
}