var selectedTours = {}

$(document).ready(function () {

    autocompleteLocations(document.querySelector('.hotel-location'), 'tourism_portal.api.query.get_locations');

    formatSelect2()
    formatDataPicker()
});

function formatSelect2() {
    $('.select2-select').each(function (i, select) {
        var icons = $(this).siblings('i');
        var labels = $(this).siblings('label');
        var placeholder = '';
        if (icons.length > 0) {
            placeholder += $(this).siblings('i').prop('outerHTML');
            $(this).siblings('i').hide();
        }
        if (labels.length > 0) {
            placeholder += $(this).siblings('label').prop('outerHTML');
            $(this).siblings('label').hide();
        }
        $(this).select2({
            theme: 'bootstrap-5',
            placeholder: placeholder,
            escapeMarkup: function (markup) {
                return markup;
            },
            templateResult: formatState
        });
        $(this).on("select2:open", function (e) { 
                document.querySelector('.select2-search__field').focus()
            });
    })

    function formatState(state) {
        if (!state.id) { return state.text; }
        var doctype = state.element.getAttribute('doc-type')
        var icon = "";
        if (doctype == 'area') {
            icon = '<i class="fa fa-map tm-color-primary"></i>'
        } else if (doctype == 'hotel') {
            icon = '<i class="fa fa-hotel tm-color-primary"></i>'
        } else if (doctype == 'airport') {
            icon = '<i class="fa fa-plane tm-color-primary"></i>'
        } else {

        }
        var $state = $(
            '<span> ' + icon +
            state.text + '</span>'
        );
        return $state;
    };
}

// Date Picker
function formatDataPicker(template, onchange) {
    if (template) {
        template.querySelectorAll('.date-picker').forEach(datePickerInput => {
            datepicker(datePickerInput, {
                formatter: (input, date, instance) => {
                    const value = date.toLocaleDateString("fr-CA")
                    input.value = value // => '1/1/2099',
                },
                onSelect:  onchange,
                
                minDate: new Date()
            });

        })
        return;
    }
    $('.date-picker').each(function (i, select) {
        datepicker(this, {
            formatter: (input, date, instance) => {
                const value = date.toLocaleDateString("fr-CA")
                input.value = value // => '1/1/2099'
            },
            onSelect:  onchange,
            minDate: new Date()
        });

    })

}

$('.room-select').change(function (e) {
    var roomCount = $(this).val();

})

function romCountChanged(e) {
    if (!e.value) e.value = 0;
    var paxContainer = e.parentNode.parentNode.querySelector('.pax-container');
    var html = '';
    for (var i = 0; i < e.value; i++) {
        document.querySelector('.pax-template-container .room-label').innerText = `Room ${i + 1}`
        html += document.querySelector('.pax-template-container').innerHTML;
    }
    paxContainer.innerHTML = html;
}
function childCountChanged(e) {
    if (!e.value) e.value = 0;
    var childrenContainer = e.parentNode.parentNode.querySelector('.children-container');
    var html = '';
    for (var i = 0; i < e.value; i++) {
        document.querySelector('.children-template-container .child-label').innerText = `Child ${i + 1}`
        html += document.querySelector('.children-template-container').innerHTML;
    }
    childrenContainer.innerHTML = html;
}
function collapseBtnPressed(e) {
    var deleteBtn = e.parentNode.querySelector('.remove-card-btn');
    if (e.parentNode.querySelector('.panel-collapse').classList.toggle('show')) {
        e.innerHTML = `<i class="fa fa-chevron-down" aria-hidden="true"></i>`
        deleteBtn.style.display = 'block';
    } else {
        e.innerHTML = `<i class="fa fa-chevron-up" aria-hidden="true"></i>`
        deleteBtn.style.display = 'none';
    }

}

function addTransferClicked(e) {
    var childrenContainer = e.closest('.voucher-search').querySelector('.transfer-search-container');
    if (childrenContainer.innerHTML.trim()) {
        return;
    }
    var html = '';
    var hotelCard = e.closest('.voucher-search').querySelector('.hotel-search-card');
    var hotelData = getHotelSearchInfo(hotelCard);
    var transferCards = document.querySelectorAll('.transfer-search-card').length + 1;
    var trnasferCardName = `Transfer Search ${transferCards}`
    var transferTemplate = document.querySelector('#transfer-search-template');
    html += transferTemplate.innerHTML;
    childrenContainer.innerHTML = html;
    var transferRows = childrenContainer.querySelectorAll('.transfer-search-row');
    var adults = 0;
    var children = 0;
    var childrenAges = [];
    for (var pax in hotelData.paxInfo) {
        adults += parseInt(hotelData.paxInfo[pax].adults);
        children += parseInt(hotelData.paxInfo[pax].children);
        childrenAges = childrenAges.concat(hotelData.paxInfo[pax].childrenInfo);
    }
    childrenContainer.querySelector('input[name="transfer-card"]').value = trnasferCardName;
    var dropoffInput = null;
    var pickupInput = null;

    for (var i = 0; i < transferRows.length; i++) {
        var transferRow = transferRows[i];

        if (i == 0) {
            dropoffInput = transferRow.querySelector('input[name="dropoff"]')

            if (hotelData['location-type'] != 'town') {
                if (hotelData.location){
                    dropoffInput.value = hotelData['location-name']
                    dropoffInput.setAttribute('location-id', hotelData.location);
                    dropoffInput.setAttribute('location-type', hotelData['location-type']);
                    dropoffInput.setAttribute('location-name', hotelData['location-name']);
                }
                
            }
            if(hotelData.checkin)
            transferRow.querySelector('input[name="check-in"]').value = hotelData.checkin;
        } else {
            pickupInput = transferRow.querySelector('input[name="pickup"]')
            if (hotelData['location-type'] != 'town') {
                if (hotelData.location){
                   pickupInput.value = hotelData['location-name'];//hotelData.location;
                pickupInput.setAttribute('location-id', hotelData.location);
                pickupInput.setAttribute('location-type', hotelData['location-type']); 
                pickupInput.setAttribute('location-name', hotelData['location-name']);
                }
                
            }

            if(hotelData.checkout)
            transferRow.querySelector('input[name="check-in"]').value = hotelData.checkout;
        }
        autocompleteLocations(transferRow.querySelector('input[name="dropoff"]'), 'tourism_portal.api.query.get_transfer_locations', (element) => {
            checkRegularFlights(element, 'departure')
        });
        autocompleteLocations(transferRow.querySelector('input[name="pickup"]'), 'tourism_portal.api.query.get_transfer_locations', (element) => {
            checkRegularFlights(element, 'arrival')
        });
        formatDataPicker(transferRow)
        transferRow.querySelector('select[name="adult"]').value = adults;
        var childsInput = transferRow.querySelector('select[name="children"]');
        childsInput.value = children;
        var event = new Event('change');
        childsInput.dispatchEvent(event);
        var agesInput = transferRow.querySelectorAll('select[name="child-age"]');
        for (var j = 0; j < agesInput.length; j++) {
            agesInput[j].value = childrenAges[j];
        }

    }

    //childrenContainer.querySelector('.round-trip').bootstrapToggle()
    e.style.display = 'none';

}
function addTourClicked(e) {
    var childrenContainer = e.closest('.voucher-search').querySelector('.tour-search-container');
    if (childrenContainer.innerHTML.trim()) {
        return;
    }
    var hotelCard = e.closest('.voucher-search').querySelector('.hotel-search-card');
    var hotelData = getHotelSearchInfo(hotelCard);
    var toursCard = document.querySelectorAll('.tour-search-card').length + 1;
    var tourCardName = `Tour ${toursCard}`
    var html = '';
    var tourTemplate = document.querySelector('#tour-search-template');
    html += tourTemplate.innerHTML;
    childrenContainer.innerHTML = html;
    var locationInput = childrenContainer.querySelector('input[name="location"]')
    if (hotelData['location-type'] != 'town') {
        if(hotelData.location){
            locationInput.value = hotelData['location-name']
            locationInput.setAttribute('location-id', hotelData.location);
            locationInput.setAttribute('location-name', hotelData['location-name']);
            locationInput.setAttribute('location-type', hotelData['location-type']);
        }
       
    }
    autocompleteLocations(locationInput, 'tourism_portal.api.query.get_tour_locations', (element)=> {
        tourTypeChanged(locationInput)
    });
    if(hotelData.checkin){
        childrenContainer.querySelector('input[name="check-in"]').value = addDays(hotelData.checkin, 1);
    }
    if(hotelData.checkout){
        childrenContainer.querySelector('input[name="check-out"]').value = addDays(hotelData.checkout, -1);
    }
    
    childrenContainer.querySelector('input[name="tour-card"]').value = tourCardName;
    var adults = 0;
    var children = 0;
    var childrenAges = [];
    for (var pax in hotelData.paxInfo) {

        adults += parseInt(hotelData.paxInfo[pax].adults);
        children += parseInt(hotelData.paxInfo[pax].children);
        childrenAges = childrenAges.concat(hotelData.paxInfo[pax].childrenInfo);
    }
    childrenContainer.querySelector('select[name="adult"]').value = adults;
    var childsInput = childrenContainer.querySelector('select[name="children"]');
    childsInput.value = children;
    var event = new Event('change');
    childsInput.dispatchEvent(event);
    var agesInput = childrenContainer.querySelectorAll('select[name="child-age"]');
    for (var i = 0; i < agesInput.length; i++) {
        agesInput[i].value = childrenAges[i];
    }
    formatDataPicker(childrenContainer, (instance, date)=>{
        tourTypeChanged(locationInput)
    })
    e.style.display = 'none';
    formatSelect2()
    selectedTours[tourCardName] = {}
}
function addDays(date, days) {
    var result = new Date(date);
    result.setDate(result.getDate() + days);
    return result.toLocaleDateString("fr-CA");
}
function addHotelClicked(e) {
    var container = $('.search-cards');


    var html = '';
    var resultItem = $('#hotel-search-template').html()
    html += resultItem//document.querySelector('.hotel_search_template').innerHTML;
    // Add a new element next to the selected last element

    container.append(html);
    var cardName = `Hotel Search ${container.find('.hotel-search-card').length}`
    container.find('.hotel-search-card:last').find('input[name="hotel-card"]').val(cardName);
    var allHotelSearchCards = document.querySelectorAll('.hotel-search-card')
    formatDataPicker(allHotelSearchCards[allHotelSearchCards.length - 1])
    formatSelect2()
    autocompleteLocations(allHotelSearchCards[allHotelSearchCards.length - 1].querySelector('.hotel-location'), 'tourism_portal.api.query.get_locations');
    // var html = '';
    // html += document.querySelector('.transfer-search-template').innerHTML;
    // childrenContainer.innerHTML = html;
    // e.style.display = 'none';

}
function pickupTransferChanged(e) {
    //checkRegularFlights(e, 'departure')
}
function checkRegularFlights(e, type) {
    var locationType = e.querySelector('input').getAttribute('location-type')//options[e.selectedIndex].getAttribute('doc-type');
    var location = e.querySelector('input').getAttribute('location-id')
    var transferRow = e.closest('.transfer-search-row')
    var transferSearch = e.closest('.transfer-search-card').querySelector('input[name="transfer-card"]').value;
    var selectName = transferSearch + transferRow.getAttribute('transfer-way') 
    if (locationType == 'airport') {
        //e.closest('.transfer-search-row').querySelector('.allowed-flights').style.display = 'block';
        //);
        frappe.call({
            "method": "tourism_portal.api.home.get_regular_flights",
            "args": {
                "location": location,
                "route": type
            },
            "callback": function (r) {
                var allowedFlights = transferRow.querySelector('.allowed-flights-list');
                var html = '';
                for (var flight of r.message) {
                    //html += `<li value="${flight.name}">${flight.name}</li>`;
                    html += `<input type="radio" name="${selectName}" value="${flight.name}" id="${selectName}-${flight.name}"> <label for="${selectName}-${flight.name}">${flight.name}</label><br>`
                }
                allowedFlights.innerHTML = html;
            }
        })
    }
}
function dropoffTransferChanged(e) {
    // checkRegularFlights(e, 'arrival');
}
function searchBtnClicked(e) {
    var hotelParams = getHotelParams();
    var transferParams = getTransferParams();
    var toursParams = getToursParams();
    var searchParams = {
        "hotelParams": hotelParams,
        "transferParams": transferParams,
        "toursparams": toursParams,
    }
    frappe.call({
        "method": "tourism_portal.api.home.create_search",
        "args": {
            "hotelParams": hotelParams,
            "transferParams": transferParams,
            "tourParams": toursParams,
        },
        callback: function (r) {
            if (r.message && r.message.is_success){
                window.open(`search?search=${r.message.search_name}`, '_self');
            }else{
                frappe.throw(r.message.message)
            }
        }
    })
    // const paramsJSON = JSON.stringify(searchParams);
    // window.open(`search?params=${encodeURIComponent(paramsJSON)}`, '_self');

    // console.log(new URLSearchParams().toString());
}

function getToursParams() {
    var tourCards = document.querySelectorAll('.tour-search-card');
    var tourParams = {}
    tourCards.forEach(tour => {
        var tourCardNumber = tour.querySelector('input[name="tour-card"]').value;
        var params = getTourData(tour, true);
        validateAllToursSelected(params, tour)
        //params['tours'] = selectedTours[tourCardNumber];
        tourParams[tourCardNumber] = params;
    })
    return tourParams;
}

function getHotelParams() {
    var hotelCards = document.querySelectorAll('.hotel-search-card');
    var hotelParams = {}
    hotelCards.forEach(hotel => {
        var hotelCardNumber = hotel.querySelector('input[name="hotel-card"]').value;
        hotelParams[hotelCardNumber] = getHotelSearchInfo(hotel, true);
    })
    return hotelParams;
}

function getTransferParams() {
    var transferCards = document.querySelectorAll('.transfer-search-card');
    var transferParams = {}
    transferCards.forEach(transfer => {
        var transferCardNumber = transfer.querySelector('input[name="transfer-card"]').value;
        transferParams[transferCardNumber] = getTransferSearchInfo(transfer, true);
    })
    return transferParams;
}

function getTransferSearchInfo(transferCard, validate) {
    var params = {};
    // ToDo: Validate All inputs inserted 
    var transfers = transferCard.querySelectorAll('.transfer-search-row:not(.d-none)');
    for (var i = 0; i < transfers.length; i++) {
        var transfer = transfers[i];
        var picupInput = transfer.querySelector('input[name="pickup"]');
        var dropoffInput = transfer.querySelector('input[name="dropoff"]');
        params[i] = {};
        params[i]['from-location'] = picupInput.getAttribute('location-id');
        params[i]['from-location-type'] = picupInput.getAttribute('location-type');
        params[i]['from-location-name'] = picupInput.getAttribute('location-name');
        params[i]['to-location'] = dropoffInput.getAttribute('location-id');
        params[i]['to-location-type'] = dropoffInput.getAttribute('location-type');
        params[i]['to-location-name'] = dropoffInput.getAttribute('location-name');
        params[i]['transfer-date'] = transfer.querySelector('input[name="check-in"]').value;
        params[i]['transfer-type'] = transfer.querySelector('select[name="transfer-type"]').value;
        if (params[i]['transfer-type'] == 'group') {
            var selectedFlight = transfer.querySelector('.allowed-flights-list input[type="radio"]:checked');
            if (!selectedFlight) {
                frappe.throw("Please select flight for " + params[i]['from-location-name'] + " - " + params[i]['to-location-name'] + " from allowed flights")
            }
            params[i]['selected-flight'] = selectedFlight.value;
        }
        params[i]['flight-no'] = transfer.querySelector('input[name="flight-no"]').value;
        params[i]['paxes'] = {}
        params[i]['paxes']['adults'] = Number(transfer.querySelector('select[name="adult"]').value);
        params[i]['paxes']['children'] = Number(transfer.querySelector('select[name="children"]').value);
        params[i]['paxes']['child-ages'] = []
        var ages = transfer.querySelectorAll('select[name="child-age"]');
        ages.forEach(age => {
            params[i]['paxes']['child-ages'].push(Number(age.value))
        })
    }
    if (validate){
        validateTransferSearchData(params)
    }
    return params
}

function validateTransferSearchData(params) {
    for (var transferNo in params) {
        var transfer = params[transferNo];
        if (!transfer['from-location']) {
            frappe.throw("Please select transfer pickup location")
        }
        if (!transfer['to-location']) {
            frappe.throw("Please select transfer dropoff location")
        }
        if (!transfer['transfer-date']) {
            frappe.throw("Please select transfer date")
        }
        if (!transfer['transfer-type']) {
            frappe.throw("Please select transfer type")
        }
        if (!transfer['paxes']) {
            frappe.throw("Please select transfer paxes")
        }
        if (!transfer['paxes']['adults']) {
            frappe.throw("Please select transfer adults count")
        }
    }
    return true;
}

function isDateBefore(dateString1, dateString2) {
    // Convert date strings to Date objects
    const date1 = new Date(dateString1);
    const date2 = new Date(dateString2);
  
    // Compare the dates
    return date1 < date2;
  }
  

function getHotelSearchInfo(hotel, validate) {
    var params = {};
    if (!hotel) return params
    var selectInput = hotel.querySelector('input[name="location"]');
    params['location'] = selectInput.getAttribute('location-id')
    params['location-name'] = selectInput.value

    params['location-type'] = selectInput.getAttribute('location-type')//selectInput.options[selectInput.selectedIndex].getAttribute('doc-type');
    params['nationality'] = hotel.querySelector('select[name="nationality"]').value
    params['checkin'] = hotel.querySelector('input[name="check-in"]').value
    params['checkout'] = hotel.querySelector('input[name="check-out"]').value
    if (isDateBefore( params['checkout'], params['checkin']) ){
        frappe.throw("Please check selected dates for " +  params['location-name'] )
    }
    params['room'] = hotel.querySelector('select[name="room"]').value
    var pax = hotel.querySelectorAll(".pax-search-card")
    // ToDo: Validate Same pax count selected as rooms count
    var paxInfo = []
    pax.forEach(room => {
        var roomName = room.querySelector(".room-label").innerText
        var adults = room.querySelector("select[name='adult']").value
        var children = room.querySelector("select[name='children']").value
        var childrenAges = room.querySelectorAll(".children-search-card")
        var childrenInfo = []

        childrenAges.forEach(child => {
            childrenInfo.push(child.querySelector('select[name="child-age"]').value)
        })
        paxInfo.push({ "roomName": roomName, "adults": adults, "children": children, "childrenInfo": childrenInfo })

    })
    params['paxInfo'] = paxInfo
    if (validate){
        validateHotelSearchData(params)
    }
    
    return params
}

function validateHotelSearchData(params) {
    if (!params['location']) {
        frappe.throw("Please select hotel location")
    }
    if (!params['checkin']) {
        frappe.throw("Please select hotel checkin date")
    }
    if (!params['checkout']) {
        frappe.throw("Please select hotel checkout date")
    }
    if (!params['room']) {
        frappe.throw("Please select hotel room count")
    }
    if (!params['paxInfo']) {
        frappe.throw("Please select hotel pax info")
    }
    for(var pax of params['paxInfo']){
    if (!pax['adults']) {
        frappe.throw("Please select hotel adults count")
    }
}
    if (!params['nationality']){
        frappe.throw("Please select guests' nationality")
    }

    return true;
}

function tourTypeChanged(e) {
    var tourData = getTourData(e.closest('form'));
    if (!validateTourSearchData(tourData)) {
        return;
    }
    var tourCard = e.closest('.tour-search-card').querySelector('input[name="tour-card"]').value;
    selectedTours[tourCard] = {}
    frappe.call({
        method: "tourism_portal.api.home.get_available_tours",
        args: {
            "tourData": tourData
        },
        callback: function (r) {
            var tourSelect = e.closest('form').querySelector('.tours-html-container');
            var totalDays = getTotalDays(tourData.checkin, tourData.checkout);
            tourSelect.innerHTML = '';
            tourSelect.setAttribute('total-days', totalDays);
            if (!r.message || Object.keys(r.message).length === 0) {
                tourSelect.innerHTML = '<li class="list-group-item">No Tours Found</li>'
            }
            for (var tourId in r.message) {
                var tour = r.message[tourId];
                var listElement = document.createElement("li");
                listElement.classList.add('list-group-item');
                listElement.classList.add('tour-list-item');
                var checkboxElement = document.createElement("input");
                checkboxElement.setAttribute('type', 'checkbox');
                checkboxElement.setAttribute('name', 'tours');
                checkboxElement.setAttribute('value', tour.tour_id);
                checkboxElement.setAttribute('onclick', 'onTourSelectChange(this)');
                checkboxElement.setAttribute('tour-time', tour.tour_time)
                checkboxElement.setAttribute('tour-dates', JSON.stringify(tour.tour_dates));
                var labelElement = document.createElement("label");
                labelElement.innerText = tour.tour_name;
                listElement.appendChild(checkboxElement);
                listElement.appendChild(labelElement);
                // listElement.innerHTML = `<input type="checkbox" onclick="onTourSelectChange(this)" name="tours" value="${tour.tour_id}"> <label>${tour.tour_name} </label>`;

                listElement.setAttribute('data-toggle', 'tooltip');
                listElement.setAttribute('data-placement', 'top');
                listElement.setAttribute('title', tour.tour_description);
                listElement.addEventListener('click', function (e) {
                    var checkbox = e.currentTarget.querySelector('input[type="checkbox"]');
                    checkbox.click();
                    // checkbox.checked = !checkbox.checked;
                    // onTourSelectChange(checkbox);
                });
                tourSelect.appendChild(listElement);
            }


        }

    })
}

function getTotalDays(checkin, checkout) {
    var checkinDate = new Date(checkin);
    var checkoutDate = new Date(checkout);
    var timeDiff = Math.abs(checkoutDate.getTime() - checkinDate.getTime());
    var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
    return diffDays;

}
function checkAvailablePackageDates(e) {
    var selectedTourElements = e.closest('form').querySelectorAll('input[name="tours"]:checked');
    var tourSelectContainer = e.closest('form').querySelector('.tours-html-container');
    var totalDays = Number(tourSelectContainer.getAttribute('total-days')) + 1;
    var tourTime = e.getAttribute('tour-time');
    for (var selectedTour of selectedTourElements) {
        var tourMinDate = Number(selectedTour.getAttribute('tour-time'));
        totalDays -= tourMinDate;
    }

    var tours = tourSelectContainer.querySelectorAll('input[name="tours"]:not(:checked)')
    for (var tour of tours) {
        if (Number(tour.getAttribute('tour-time')) > totalDays) {
            tour.disabled = true;
        } else {
            tour.disabled = false;
        }

    }
}
function checkAvailableIndividualDates(e) {
    var selectedTourElements = e.closest('form').querySelectorAll('input[name="tours"]:checked');
    var tourSelectContainer = e.closest('form').querySelector('.tours-html-container');
    var totalDays = Number(tourSelectContainer.getAttribute('total-days')) + 1;
    var tourTimes = {
        "morning": [],
        "evening": [],
    }

    for (var selected of selectedTourElements) {
        if (selected.getAttribute('tour-time') == 'Half Day Morning') {
            if (tourTimes['evening'].length > 0) {
                tourTimes['evening'].pop()
                totalDays += 1;
            } else {
                tourTimes['morning'].push(selected.value)
            }

        } else if (selected.getAttribute('tour-time') == 'Half Day Evening') {
            if (tourTimes['morning'].length > 0) {
                tourTimes['morning'].pop()
                totalDays += 1;
            }
            else {
                tourTimes['evening'].push(selected.value)
            }
        }

    }
    if (selectedTourElements.length >= totalDays) {
        var tours = tourSelectContainer.querySelectorAll('input[name="tours"]:not(:checked)')
        
        for (var tour of tours) {
            if (tour.getAttribute('tour-time')== 'Half Day Morning' && tourTimes['evening'].length == 0) {
                tour.disabled = true;
            } else if (tour.getAttribute('tour-time')== 'Half Day Evening' && tourTimes['morning'].length == 0) {
                tour.disabled = true;
            }
            else if (tour.getAttribute('tour-time')== 'Half Day Morning' && tourTimes['evening'].length > 0) {
                tour.disabled = false;
            } else if (tour.getAttribute('tour-time')== 'Half Day Evening' && tourTimes['morning'].length > 0) {
                tour.disabled = false;
            }else{
                tour.disabled = true;
            }
            
        }
    } else {
        var tours = tourSelectContainer.querySelectorAll('input[name="tours"]:not(:checked)')
        for (var tour of tours) {
            tour.disabled = false;
        }
    }
}

function onTourSelectChange(e) {
    var tourCard = e.closest('.tour-search-card').querySelector('input[name="tour-card"]').value;


    var tourType = e.closest('form').querySelector('select[name="tour-type"]').value;

    if (tourType == 'package') {
        checkAvailablePackageDates(e)
    } else {
        checkAvailableIndividualDates(e)
    }

    var tourDates = JSON.parse(e.getAttribute('tour-dates'))
    // if (e.checked) {
    //     selectedTours[tourCard][e.value] = true;

    // }
    // else {
    //     delete selectedTours[tourCard][e.value];

    // }
    // if(e.closest('form').querySelector('select[name="tour-type"]').value != 'vip'){
    //     checkOverlappingTours(selectedTours[tourCard], tourSelectContainer);
    // }
}
function checkOverlappingTours(selectedTours, tourSelectContainer) {
    var tourDates = Object.keys(selectedTours);
    var tourElements = tourSelectContainer.querySelectorAll('input[name="tours"]');
    for (var tourElement of tourElements) {
        var tourElementDates = JSON.parse(tourElement.getAttribute('tour-dates'));
        var allIncluded = true;
        for (var tourElementDate of tourElementDates) {
            if (!tourDates.includes(tourElementDate)) {
                allIncluded = false;
            }
        }
        if (allIncluded && !tourElement.checked) {
            tourElement.disabled = true;
        }
    }
}
function bindToolTipElement(element, toolTipElement) {
    // Event listener for the select element
    var toolTip = toolTipElement
    element.addEventListener('mouseover', function (event) {
        var targetOption = event.target;
        if (targetOption.dataset.tooltip) {
            toolTip.style.display = 'block';

            // Position tooltip next to the option
            // var optionRect = targetOption.getBoundingClientRect();
            // tooltipElement.style.top = optionRect.bottom + 'px';
            // tooltipElement.style.left = optionRect.left + 'px';
        }
    });

    // Hide tooltip when mouse leaves the select element
    element.addEventListener('mouseout', function () {
        toolTip.style.display = 'none';
    });
}
function validateTourSearchData(tourData) {
    if (!tourData['location']) {
        return false;
    }
    if (!tourData['checkin']) {
        return false;
    }
    if (!tourData['checkout']) {
        return false;
    }
    if (!tourData['tour-type']) {
        return false;
    }
    return true;
}
function transferTypeChanged(e) {
    if (e.value == 'group') {
        e.closest('form').querySelector('.allowed-flights').style.display = 'block';
    } else {
        e.closest('form').querySelector('.allowed-flights').style.display = 'none';
    }
}
function getTourData(form, validate) {
    var params = {};
    var locationInput = form.querySelector('input[name="location"]');
    params['location-name'] = locationInput.value
    params['location'] = locationInput.getAttribute('location-id')
    params['location-type'] = locationInput.getAttribute('location-type')//form.querySelector('select[name="location"]').options[form.querySelector('select[name="location"]').selectedIndex].getAttribute('doc-type');
    params['checkin'] = form.querySelector('input[name="check-in"]').value
    params['checkout'] = form.querySelector('input[name="check-out"]').value
    if (isDateBefore( params['checkout'], params['checkin']) ){
        frappe.throw("Please check selected dates for " +  params['location-name'] )
    }
    params['paxes'] = {}
    params['paxes']['adults'] = form.querySelector('select[name="adult"]').value
    params['paxes']['children'] = form.querySelector('select[name="children"]').value
    params['paxes']['child-ages'] = []
    var ages = form.querySelectorAll('select[name="child-age"]');
    ages.forEach(age => {
        params['paxes']['child-ages'].push(age.value)
    })
    params['tour-type'] = form.querySelector('select[name="tour-type"]').value
    params['tours'] = []
    form.querySelectorAll('input[name="tours"]:checked').forEach(tour => {
        params['tours'].push(tour.value)
    })
    if (validate){
        validateCardTourSearchData(params)
    }

    // params['tour-name'] = form.querySelector('select[name="tour-name"]').value
    return params;
}

function validateCardTourSearchData(params) {
    if (!params['location']) {
        frappe.throw("Please select tour location")
    }
    if (!params['checkin']) {
        frappe.throw("Please select tour checkin date")
    }
    if (!params['checkout']) {
        frappe.throw("Please select tour checkout date")
    }
    if (!params['paxes']) {
        frappe.throw("Please select tour paxes")
    }
    if (!params['paxes']['adults']) {
        frappe.throw("Please select tour adults count")
    }
    if (!params['tour-type']) {
        frappe.throw("Please select tour type")
    }
    if (params['tours'].length == 0) {
        frappe.throw("Please select tour")
    }
    return true;
}

function validateAllToursSelected(params, form) {
    // var totalDays = getTotalDays(params['checkin'], params['checkout']) + 1;
    // if (params['tours'].length > totalDays) {
    //     msgprint('You can select only one tour per day')
    //     throw new Error('You can select only one tour per day');
    //     return false;
    // } else if (params['tours'].length < totalDays && form.querySelectorAll('.tour-list-item').length > params['tours'].length) {
    //     msgprint('You must select a tour for each day')
    //     throw new Error('You must select a tour for each day');
    //     return false;
    // }
}

function onlyTransferClicked(e) {
    document.querySelectorAll('.hotel-search-container').forEach(hotel => {
        hotel.innerHTML = '';
    })
    document.querySelectorAll('.tour-search-container').forEach(hotel => {
        hotel.innerHTML = '';
    })
    addTransferClicked(document.querySelector('.hotel-search-container'));
}
function onlyTourClicked(e) {
    document.querySelectorAll('.hotel-search-container').forEach(hotel => {
        hotel.innerHTML = '';
    })
    document.querySelectorAll('.transfer-search-container').forEach(hotel => {
        hotel.innerHTML = '';
    })
    addTourClicked(document.querySelector('.hotel-search-container'));
}

function tourAddTourClicked(e) {
   var previousCard = e.closest('.search-card-container')
   var toursContainer = e.closest('.tour-search-continer-with-more')
   var moreTourContainer = toursContainer.querySelector('.more-tour')
   var params = getTourData(previousCard);
   var toursCard = document.querySelectorAll('.tour-search-card').length + 1;
   var tourCardName = `Tour ${toursCard}`
   var html = '';
    var tourTemplate = document.querySelector('#tour-search-template');
    html += tourTemplate.innerHTML;
    moreTourContainer.innerHTML = html;
    var locationInput = moreTourContainer.querySelector('input[name="location"]')
    if(params.location){
        locationInput.value = params['location-name']
        locationInput.setAttribute('location-id', params.location);
        locationInput.setAttribute('location-name', params['location-name']);
        locationInput.setAttribute('location-type', params['location-type']);
    }
    autocompleteLocations(locationInput, 'tourism_portal.api.query.get_tour_locations',(element)=> {
        tourTypeChanged(locationInput)
    });
    if(params.checkout){
        moreTourContainer.querySelector('input[name="check-in"]').value = addDays(params.checkout, 1);
    }
    moreTourContainer.querySelector('input[name="check-out"]').addEventListener('change', function(e){
    })
    moreTourContainer.querySelector('input[name="tour-card"]').value = tourCardName;
    var adults = params.paxes.adults;
    var children = params.paxes.children;
    var childrenAges = params.paxes['child-ages'];
    moreTourContainer.querySelector('select[name="adult"]').value = adults;
    var childsInput = moreTourContainer.querySelector('select[name="children"]');
    childsInput.value = children;
    var event = new Event('change');
    childsInput.dispatchEvent(event);
    var agesInput = moreTourContainer.querySelectorAll('select[name="child-age"]');
    for (var i = 0; i < agesInput.length; i++) {
        agesInput[i].value = childrenAges[i];
    }

    formatDataPicker(moreTourContainer, (instance, date)=>{
        tourTypeChanged(locationInput)
    })
    e.style.display = 'none';
}

function onWayTransfer(e){
    var transferCard = e.closest('.transfer-search-card')
    var dataWay = e.getAttribute("data-way")
    if (dataWay == 'one-way'){
        // transferCard.querySelector('.return-transfer').style.display = 'none';
        transferCard.querySelector('.return-transfer').classList.add('d-none');
        e.setAttribute("data-way", "two-way")
        e.innerHTML = `<i class="fa fa-exchange" aria-hidden="true"></i> Two Way`

    }else{
        // transferCard.querySelector('.return-transfer').style.display = 'block';
        transferCard.querySelector('.return-transfer').classList.remove('d-none');
        e.setAttribute("data-way", "one-way")
        e.innerHTML = `<i class="fa fa-exchange" aria-hidden="true"></i> One Way`
    }
}

function transferAddTransferClicked(e){
    var previousCard = e.closest('.search-card-container')
   var transfersContainer = e.closest('.transfer-search-continer-with-more')
   var moreTransferContainer = transfersContainer.querySelector('.more-transfer')
   var params = getTransferSearchInfo(previousCard);

   var transferCards = document.querySelectorAll('.transfer-search-card').length + 1;

   var trnasferCardName = `Transfer Search ${transferCards}`

   var html = '';
    var transferTemplate = document.querySelector('#transfer-search-template');
    html += transferTemplate.innerHTML;
    moreTransferContainer.innerHTML = html;
    var transferRows = moreTransferContainer.querySelectorAll('.transfer-search-row');
    moreTransferContainer.querySelector('input[name="transfer-card"]').value = trnasferCardName;
    var paxes = null;
    if (Object.keys(params).length > 0){
        paxes = params[Object.keys(params)[0]]['paxes'];
    }
    for (var i = 0; i < transferRows.length; i++) {
        var transferRow = transferRows[i];
        if (i == 0) {
            dropoffInput = transferRow.querySelector('input[name="dropoff"]')

        } else {
            pickupInput = transferRow.querySelector('input[name="pickup"]')
        }

        autocompleteLocations(transferRow.querySelector('input[name="dropoff"]'), 'tourism_portal.api.query.get_transfer_locations', (element) => {
            checkRegularFlights(element, 'departure')
        });
        autocompleteLocations(transferRow.querySelector('input[name="pickup"]'), 'tourism_portal.api.query.get_transfer_locations', (element) => {
            checkRegularFlights(element, 'arrival')
        });
        formatDataPicker(transferRow)
        if (paxes){
            transferRow.querySelector('select[name="adult"]').value = paxes.adults;
            var childsInput = transferRow.querySelector('select[name="children"]');
            childsInput.value = paxes.children;
            var event = new Event('change');
            childsInput.dispatchEvent(event);
            var agesInput = transferRow.querySelectorAll('select[name="child-age"]');
            for (var j = 0; j < agesInput.length; j++) {
                agesInput[j].value = paxes['child-ages'][j];
            }
        }
        

    }

    e.style.display = 'none';
}


function deleteBtnPressed(e){
    frappe.confirm(
        'Are you sure you want to delete this card?',
        function () {
            deleteCard(e)
        },
        function () {
            console.log('No')
        }
    )
   
}

function deleteCard(e){
    var card = e.closest('.search-card-container')
    var cardType = card.getAttribute('card-type');
    if (cardType == 'hotel'){
        card.remove();
    }else if (cardType == 'transfer'){
        card.remove();
    }else if (cardType == 'tour'){
        card.remove();
    }
    renumberCards();
}

function renumberCards(){
    var hotelCards = document.querySelectorAll('.hotel-search-card');
    var transferCards = document.querySelectorAll('.transfer-search-card');
    var tourCards = document.querySelectorAll('.tour-search-card');
    var i = 1;
    hotelCards.forEach(hotelCard => {
        hotelCard.querySelector('input[name="hotel-card"]').value = `Hotel Search ${i}`
        i++;
    })
    i = 1;
    transferCards.forEach(transferCard => {
        transferCard.querySelector('input[name="transfer-card"]').value = `Transfer Search ${i}`
        i++;
    })
    i = 1;
    tourCards.forEach(tourCard => {
        tourCard.querySelector('input[name="tour-card"]').value = `Tour ${i}`
        i++;
    })
}