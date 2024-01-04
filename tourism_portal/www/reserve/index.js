var paxesNames = {}

var sessionTimer = document.getElementById('session-timer')
if (sessionTimer){
// Set the countdown time in seconds
var dateObject = new Date(sessionTimer.getAttribute("datetime"));
var currentDate = new Date();

// Calculate the difference in milliseconds
var timeDifference = dateObject.getTime() - currentDate.getTime();

const countdownTime = Math.round(Math.max(timeDifference / 1000, 0)); // 5 minutes
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

document.querySelectorAll(".adult-pax").forEach((e) => {
  var paxName = "adult-" + e.getAttribute("adult-pax")
  paxesNames[paxName] = {
    "name": "",
    "salut": ""
  }
})
document.querySelectorAll(".child-pax").forEach((e) => {
  var paxName = "child-" + e.getAttribute("child-pax")
  paxesNames[paxName] = {
    "name": "",
    "salut": ""
  }
})

function adultSalutChanged(e){
  var paxContainer = e.closest(".pax-container")
  if (paxContainer.classList.contains("adult-pax-diff")){
    return
  }
  var paxName = "adult-" + paxContainer.getAttribute("adult-pax")
  paxesNames[paxName]["salut"] = e.value
  notifiyPaxName(paxName)
}
function adultPaxChanged(e){
  var paxContainer = e.closest(".pax-container")
  if (paxContainer.classList.contains("adult-pax-diff")){
    return
  }

  var paxName = "adult-" + paxContainer.getAttribute("adult-pax")
  paxesNames[paxName]["name"] = e.value
  notifiyPaxName(paxName)
}

function childPaxChanged(e){
  var paxContainer = e.closest(".pax-container")
  if (paxContainer.classList.contains("child-pax-diff")){
    return
  }
  var paxName = "child-" + paxContainer.getAttribute("child-pax")
  paxesNames[paxName]["name"] = e.value
  notifiyPaxName(paxName)
}

function notifiyPaxName(paxName){
  var paxType = paxName.split("-")[0]
  if (paxType == "adult"){
    var paxNumber = paxName.split("-")[1]
    var paxNameElements = document.querySelectorAll(`.adult-pax[adult-pax="${paxNumber}"]`)
    for (var paxNameElement of paxNameElements){
      var nameInput = paxNameElement.querySelector("input[name='pax-name']")
      var salutInput = paxNameElement.querySelector("select[name='pax-salut']")
      nameInput.value = paxesNames[paxName].name
      salutInput.value = paxesNames[paxName].salut
    }
  }else if (paxType == "child"){
    var paxNumber = paxName.split("-")[1]
    var paxNameElements = document.querySelectorAll(`.child-pax[child-pax="${paxNumber}"]`)
    for (var paxNameElement of paxNameElements){
      var nameInput = paxNameElement.querySelector("input[name='pax-name']")
      nameInput.value = paxesNames[paxName].name
    }
  }
}

function roomBoardChanged(e){
  var totalNights = e.closest('.hotel-reservation_details').getAttribute('total-nights')
  var boardPrice = e.getAttribute('extra-price')
}

function validateReservationData(){
    var customerInput = $("input[name='customer-name']")
    var emailInput = $("input[name='email']")
    var phoneInput = $("input[name='phone-number']")
    var uncompleatedForm = false;
    uncompleatedForm = validateInput(customerInput) ? uncompleatedForm: true;
    uncompleatedForm = validateInput(emailInput) ? uncompleatedForm: true;
    uncompleatedForm = validateInput(phoneInput) ? uncompleatedForm: true;
    $("select[name='pax-salut']").each(function(index, element) {
      if (element)
        uncompleatedForm = validateInput($(element)) ? uncompleatedForm: true;
    })
    $("input[name='pax-name']").each(function(index, element) {
      if (element)
        uncompleatedForm = validateInput($(element)) ? uncompleatedForm: true;
    })
    uncompleatedForm = validateRadioInputSelected('room-bed-list') ? uncompleatedForm: true;
    uncompleatedForm = validateRadioInputSelected('room-board-list') ? uncompleatedForm: true;
    if (uncompleatedForm){
      frappe.throw("Please complete all required fields!")
    }
}
function validateInput(input){
  if(!input.val()){
    input.addClass('is-invalid');
    return false;
  }else{
    input.removeClass('is-invalid');
    return true;
  }
}
function validateRadioInputSelected(className){
  var uncompleatedForm = false;
  $(`.${className}`).each(function(){
    var listElement = $(this)
    listElement.css('border', '');
    var listName = listElement.find('input[type="radio"]').attr('name')
    if (!$('input[name="' + listName  + '"]:checked').length){
      uncompleatedForm = true;
      listElement.css('border', '2px solid red');
    }
  })
  return !uncompleatedForm
}
function confirmReservationButtonClicked(e){
  validateReservationData();
  var customerName = document.querySelector('input[name="customer-name"]').value
  var customerEmail = document.querySelector('input[name="email"]').value
  var customerMobile = document.querySelector('input[name="phone-number"]').value
  var roomsInfo = getRoomsInfo()
  var toursInfo = getToursInfo()
  var transferInfo = getTransferInfo()
  var searchParams = new URLSearchParams(window.location.search)
  var invoice = searchParams.get("invoice")
  frappe.call({
    method: "tourism_portal.api.reserve.complete_reservation",
    args: {
      sales_invoice: invoice,
      rooms: roomsInfo,
      tours: toursInfo,
      transfers: transferInfo,
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

function getTransferInfo(){
  var transfers = document.querySelectorAll(".transfer-search-container")
  var transfersInfo = {};
  for (var transfer of transfers){
    var paxes = transfer.querySelectorAll(".pax-container")
    var transferSearch = transfer.getAttribute("search-name")
    var transferName = transfer.getAttribute("transfer-name")
    if (! transfersInfo[transferSearch]){
      transfersInfo[transferSearch] = {}
    }
    transfersInfo[transferSearch][transferName] = {
      "transfer_name": transferName,
      "transfer_search": transferSearch,
      "paxes": {}
    }
    var flightNo = transfer.querySelector('input[name="flight-no"]').value
    transfersInfo[transferSearch][transferName]['flight_no'] = flightNo
    for (var pax of paxes){
      var salutInput = pax.querySelector('select[name="pax-salut"]');
      var salut = ""
      if (salutInput){
        // ToDo show Error if empty
        salut = salutInput.value
      }
      transfersInfo[transferSearch][transferName]['paxes'][pax.getAttribute('row-id')] = {
        "salut": salut,
        "guest_name": pax.querySelector('input[name="pax-name"]').value,
        "row_id": pax.getAttribute("row-id")
      }
    }
  }
  return transfersInfo;
}

function getToursInfo(){
  var tours = document.querySelectorAll(".tour-search-container")
  var toursInfo = {};
  for (var tour of tours){
    var paxes = tour.querySelectorAll(".pax-container")
    toursInfo[tour.getAttribute('search-name')] = {}
    for (var pax of paxes){
      var salutInput = pax.querySelector('select[name="pax-salut"]');
      var salut = ""
      if (salutInput){
        // ToDo show Error if empty
        salut = salutInput.value
      }
      toursInfo[tour.getAttribute('search-name')][pax.getAttribute('row-id')] = {
        "salut": salut,
        "guest_name": pax.querySelector('input[name="pax-name"]').value,
        "row_id": pax.getAttribute("row-id")
      }
    }
  }
  return toursInfo;
}

function getRoomsInfo(){
  var rooms = document.querySelectorAll(".hotel_room_container")

  var roomsInfo = {};
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
    var selectedBoard =room.querySelector('.board-input:checked')
    var selectedBed =room.querySelector('.bed-input:checked')
    roomsInfo[room.getAttribute('row-id')]['details'] = {
      "board": selectedBoard.value,
      "board_price": selectedBoard.getAttribute('extra-price'),
    }
    if (selectedBed){
      roomsInfo[room.getAttribute('row-id')]['details']['bed_type'] = selectedBed.value
    }
  }
  return roomsInfo;
}

function different_names_clicked(e){
  var card = e.closest(".card-details")
  
  if (e.checked){
    var adult_paxes = card.querySelectorAll(".adult-pax")
  var child_paxes = card.querySelectorAll(".child-pax")
    for (var pax of adult_paxes){
      pax.classList.remove("adult-pax")
      pax.classList.add("adult-pax-diff")
    }
    for (var pax of child_paxes){
      pax.classList.remove("child-pax")
      pax.classList.add("child-pax-diff")
    }
  }else{
    var adult_paxes = card.querySelectorAll(".adult-pax-diff")
  var child_paxes = card.querySelectorAll(".child-pax-diff")
    for (var pax of adult_paxes){
      pax.classList.remove("adult-pax-diff")
      pax.classList.add("adult-pax")
    }
    for (var pax of child_paxes){
      pax.classList.remove("child-pax-diff")
      pax.classList.add("child-pax")
    }
  }
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
  var totalAmount = Number( document.querySelector(`#${totalId}`).innerText.replaceAll(",", "."));
  document.querySelector(`#${totalId}`).innerText = totalAmount + Number(amount)
  updateGrandTotal()
}

function updateGrandTotal(){
  var hotelFees = Number(document.querySelector('#hotel_fees').innerText.replaceAll(",", "."))
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