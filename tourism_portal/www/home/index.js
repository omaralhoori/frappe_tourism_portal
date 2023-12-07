var selectedTours = {}

$(document).ready(function () {
    formatSelect2()
    formatDataPicker()
});

function formatSelect2(){
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
    })

    function formatState (state) {
        if (!state.id) { return state.text; }
        var doctype = state.element.getAttribute('doc-type')
        var icon = "";
        if (doctype == 'area'){
            icon = '<i class="fa fa-map tm-color-primary"></i>'
        }else if (doctype == 'hotel'){
            icon = '<i class="fa fa-hotel tm-color-primary"></i>'
        }else if (doctype == 'airport'){
            icon = '<i class="fa fa-plane tm-color-primary"></i>'
        }else{
            
        }
        var $state = $(
          '<span> ' + icon +  
      state.text +     '</span>'
       );
       return $state;
      };
}

// Date Picker
function formatDataPicker(template){
    
        $('.date-picker').each(function (i, select) {
            datepicker(this, {
                formatter: (input, date, instance) => {
                    const value = date.toLocaleDateString("fr-CA")
                    input.value = value // => '1/1/2099'
                }
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
    if (e.parentNode.querySelector('.panel-collapse').classList.toggle('show')){
        e.innerHTML = `<i class="fa fa-chevron-down" aria-hidden="true"></i>`
    }else{
        e.innerHTML = `<i class="fa fa-chevron-up" aria-hidden="true"></i>`
    }
    
}

function addTransferClicked(e) {
    var childrenContainer = e.closest('.voucher-search').querySelector('.transfer-search-container');
    if (childrenContainer.innerHTML.trim()){
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
    for (var pax in hotelData.paxInfo){
        adults += parseInt(hotelData.paxInfo[pax].adults);
        children += parseInt(hotelData.paxInfo[pax].children);
        childrenAges = childrenAges.concat(hotelData.paxInfo[pax].childrenInfo);
    }
    childrenContainer.querySelector('input[name="transfer-card"]').value = trnasferCardName;

    for (var i=0; i < transferRows.length; i++){
        var transferRow = transferRows[i];

        if (i == 0){
            transferRow.querySelector('select[name="dropoff"]').value = hotelData.location  
            transferRow.querySelector('input[name="check-in"]').value = hotelData.checkin;   
        }else{
            transferRow.querySelector('select[name="pickup"]').value = hotelData.location;
            transferRow.querySelector('input[name="check-in"]').value = hotelData.checkout;
        }
       
        transferRow.querySelector('select[name="adult"]').value = adults;
        var childsInput = transferRow.querySelector('select[name="children"]');
        childsInput.value = children ;
        var event = new Event('change');
        childsInput.dispatchEvent(event);
        var agesInput = transferRow.querySelectorAll('select[name="child-age"]');
        for (var j = 0; j < agesInput.length; j++) {
            agesInput[j].value = childrenAges[j];
        }
        
    }
   
   
    e.style.display = 'none';
    formatSelect2()
}
function addTourClicked(e) {
    var childrenContainer = e.closest('.voucher-search').querySelector('.tour-search-container');
    if (childrenContainer.innerHTML.trim()){
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
    childrenContainer.querySelector('select[name="location"]').value = hotelData.location  
    childrenContainer.querySelector('input[name="check-in"]').value = addDays(hotelData.checkin, 1);   
    childrenContainer.querySelector('input[name="check-out"]').value = addDays( hotelData.checkout, -1);
    childrenContainer.querySelector('input[name="tour-card"]').value = tourCardName;
    var adults = 0;
    var children = 0;
    var childrenAges = [];
    for (var pax in hotelData.paxInfo){
    
        adults += parseInt(hotelData.paxInfo[pax].adults);
        children += parseInt(hotelData.paxInfo[pax].children);
        childrenAges = childrenAges.concat(hotelData.paxInfo[pax].childrenInfo);
    }
    childrenContainer.querySelector('select[name="adult"]').value = adults;
    var childsInput = childrenContainer.querySelector('select[name="children"]');
    childsInput.value = children ;
    var event = new Event('change');
    childsInput.dispatchEvent(event);
    var agesInput = childrenContainer.querySelectorAll('select[name="child-age"]');
    for (var i = 0; i < agesInput.length; i++) {
        agesInput[i].value = childrenAges[i];
    }
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
     container.find('.hotel-search-card:last').find('input[name="hotel-card"]').val(container.find('.hotel-search-card').length);
     formatSelect2()
     
    // var html = '';
    // html += document.querySelector('.transfer-search-template').innerHTML;
    // childrenContainer.innerHTML = html;
    // e.style.display = 'none';
    
}

function searchBtnClicked(e){
    var hotelParams = getHotelParams();
    var transferParams = getTransferParams();
    var toursParams = getToursParams();
    var searchParams = {
        "hotelParams": hotelParams,
        "transferParams": transferParams,
        "toursparams": toursParams,
    }
    const paramsJSON = JSON.stringify(searchParams);
    console.log(searchParams)
    window.open(`search?params=${encodeURIComponent(paramsJSON)}`, '_self');

    // console.log(new URLSearchParams().toString());
}

function getToursParams(){
    var tourCards = document.querySelectorAll('.tour-search-card');
    var tourParams = {}
    tourCards.forEach(tour => {
        var tourCardNumber = tour.querySelector('input[name="tour-card"]').value;
        var params = getTourData(tour); 
        validateAllToursSelected(params, tour)
        params['tours'] = selectedTours[tourCardNumber];
        tourParams[tourCardNumber] =  params;
    })
    return tourParams;
}

function getHotelParams(){
    var hotelCards = document.querySelectorAll('.hotel-search-card');
    var hotelParams = {}
    hotelCards.forEach(hotel => {
        var hotelCardNumber = hotel.querySelector('input[name="hotel-card"]').value;
        hotelParams[hotelCardNumber] =  getHotelSearchInfo(hotel);
    })
    return hotelParams;
}

function getTransferParams(){
    var transferCards = document.querySelectorAll('.transfer-search-card');
    var transferParams = {}
    transferCards.forEach(transfer => {
        var transferCardNumber = transfer.querySelector('input[name="transfer-card"]').value;
        transferParams[transferCardNumber] =  getTransferSearchInfo(transfer);
    })
    return transferParams;
}

function getTransferSearchInfo(transferCard){
    var params = {};
    // ToDo: Validate All inputs inserted 
    var transfers  = transferCard.querySelectorAll('.transfer-search-row');
    for (var i = 0; i < transfers.length; i++){
        var transfer = transfers[i];
        var picupInput  = transfer.querySelector('select[name="pickup"]');
        var dropoffInput  = transfer.querySelector('select[name="dropoff"]');
        params[i] = {};
        params[i]['from-location'] = picupInput.value;
        params[i]['from-location-type'] = picupInput.options[picupInput.selectedIndex].getAttribute('doc-type');
        params[i]['to-location'] = dropoffInput.value;
        params[i]['to-location-type'] = dropoffInput.options[dropoffInput.selectedIndex].getAttribute('doc-type');
        params[i]['transfer-date'] = transfer.querySelector('input[name="check-in"]').value;
        params[i]['transfer-type'] = transfer.querySelector('select[name="transfer-type"]').value;
        params[i]['paxes'] = {}
        params[i]['paxes']['adults'] = Number(transfer.querySelector('select[name="adult"]').value);
        params[i]['paxes']['children'] = Number( transfer.querySelector('select[name="children"]').value);
        params[i]['paxes']['child-ages'] = []
        var ages = transfer.querySelectorAll('select[name="child-age"]');
        ages.forEach(age => {
            params[i]['paxes']['child-ages'].push(Number(age.value))
        })
    }
    return params
}

function getHotelSearchInfo(hotel){
    var params = {};
    if (!hotel)return params
    // ToDo: Validate All inputs inserted 
    var selectInput =hotel.querySelector('select[name="location"]');
    params['location'] = selectInput.value

    params['location-type'] = selectInput.options[selectInput.selectedIndex].getAttribute('doc-type');
    params['nationality'] = hotel.querySelector('select[name="nationality"]').value
    params['checkin'] = hotel.querySelector('input[name="check-in"]').value
    params['checkout'] = hotel.querySelector('input[name="check-out"]').value
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
        paxInfo.push({"roomName": roomName, "adults": adults, "children": children, "childrenInfo": childrenInfo})

    })
    params['paxInfo'] = paxInfo
    return params
}

function tourTypeChanged(e){
    var tourData = getTourData(e.closest('form'));
    if (! validateTourSearchData(tourData)){
        return;
    }
    var tourCard = e.closest('.tour-search-card').querySelector('input[name="tour-card"]').value ;
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
            if (!r.message || Object.keys(r.message).length === 0){
                tourSelect.innerHTML = '<li class="list-group-item">No Tours Found</li>'
            }
            for (var tourId in r.message){
                var tour = r.message[tourId];
                var listElement = document.createElement("li");
                listElement.classList.add('list-group-item');
                listElement.classList.add('tour-list-item');
                var checkboxElement = document.createElement("input");
                checkboxElement.setAttribute('type', 'checkbox');
                checkboxElement.setAttribute('name', 'tours');
                checkboxElement.setAttribute('value', tour.tour_id);
                checkboxElement.setAttribute('onclick', 'onTourSelectChange(this)');
                checkboxElement.setAttribute('tour-dates', JSON.stringify(tour.tour_dates));
                var labelElement = document.createElement("label");
                labelElement.innerText = tour.tour_name;
                listElement.appendChild(checkboxElement);
                listElement.appendChild(labelElement);
                // listElement.innerHTML = `<input type="checkbox" onclick="onTourSelectChange(this)" name="tours" value="${tour.tour_id}"> <label>${tour.tour_name} </label>`;
                
                listElement.setAttribute('data-toggle', 'tooltip');
                listElement.setAttribute('data-placement', 'top');
                listElement.setAttribute('title', tour.tour_description);
                listElement.addEventListener('click', function(e){ 
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

function getTotalDays(checkin, checkout){
    var checkinDate = new Date(checkin);
    var checkoutDate = new Date(checkout);
    var timeDiff = Math.abs(checkoutDate.getTime() - checkinDate.getTime());
    var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 
    return diffDays;

}

function onTourSelectChange(e){
    var tourCard = e.closest('.tour-search-card').querySelector('input[name="tour-card"]').value ;
    var selectedTourElements = e.closest('form').querySelectorAll('input[name="tours"]:checked');
    var tourSelectContainer =  e.closest('form').querySelector('.tours-html-container');
    var totalDays = tourSelectContainer.getAttribute('total-days');

    if (selectedTourElements.length > totalDays){
       var tours = tourSelectContainer.querySelectorAll('input[name="tours"]:not(:checked)')
       for(var tour of tours) {
            tour.disabled = true;
        }
    }else{
        var tours = tourSelectContainer.querySelectorAll('input[name="tours"]:not(:checked)')
        for(var tour of tours){
            tour.disabled = false;
        }
    }
    var tourDates = JSON.parse(e.getAttribute('tour-dates'))
    if (e.checked){
        for (var tourDate of tourDates){
            if (!selectedTours[tourCard][tourDate]){
                selectedTours[tourCard][tourDate] = e.value;
                break;
            }
        }
    }else{
        for (var tourDate of tourDates){
            if (selectedTours[tourCard][tourDate] == e.value){
                delete selectedTours[tourCard][tourDate];
                break;
            }
        }
    }
    if(e.closest('form').querySelector('select[name="tour-type"]').value != 'vip'){
        checkOverlappingTours(selectedTours[tourCard], tourSelectContainer);
    }
}
function checkOverlappingTours(selectedTours, tourSelectContainer){
    var tourDates = Object.keys(selectedTours);
    var tourElements = tourSelectContainer.querySelectorAll('input[name="tours"]');
    for (var tourElement of tourElements){
        var tourElementDates = JSON.parse(tourElement.getAttribute('tour-dates'));
        var allIncluded = true;
        for (var tourElementDate of tourElementDates){
            if (!tourDates.includes(tourElementDate)){
               allIncluded = false;
            }
        }
        if (allIncluded && !tourElement.checked){
            tourElement.disabled = true;}
    }
}
function bindToolTipElement(element, toolTipElement){
     // Event listener for the select element
     var toolTip = toolTipElement
     element.addEventListener('mouseover', function (event) {
        var targetOption = event.target;
        if (targetOption.dataset.tooltip) {
            console.log(targetOption.dataset.tooltip);
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
function validateTourSearchData(tourData){
    if (!tourData['location']){
        return false;
    }
    if (!tourData['checkin']){
        return false;
    }
    if (!tourData['checkout']){
        return false;
    }
    if (!tourData['tour-type']){
        return false;
    }
    return true;
}
function transferTypeChanged(e){
    if (e.value == 'group'){
        e.closest('form').querySelector('.allowed-flights').style.display = 'block';
    }else{
        e.closest('form').querySelector('.allowed-flights').style.display = 'none';
    }
}
function getTourData(form){
    var params = {};
    params['location'] = form.querySelector('select[name="location"]').value
    params['location-type'] = form.querySelector('select[name="location"]').options[form.querySelector('select[name="location"]').selectedIndex].getAttribute('doc-type');
    params['checkin'] = form.querySelector('input[name="check-in"]').value
    params['checkout'] = form.querySelector('input[name="check-out"]').value
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
    
    // params['tour-name'] = form.querySelector('select[name="tour-name"]').value
    return params;
}

function  validateAllToursSelected(params, form){
    var totalDays = getTotalDays(params['checkin'], params['checkout']) + 1;
    if (params['tours'].length > totalDays){
        msgprint('You can select only one tour per day')
        throw new Error('You can select only one tour per day');
        return false;
    }else if (params['tours'].length < totalDays && form.querySelectorAll('.tour-list-item').length > params['tours'].length){
        msgprint('You must select a tour for each day')
        throw new Error('You must select a tour for each day');
        return false;
    }
}

function onlyTransferClicked(e){
    document.querySelectorAll('.hotel-search-container').forEach(hotel => {
        hotel.innerHTML = '';
    })
    document.querySelectorAll('.tour-search-container').forEach(hotel => {
        hotel.innerHTML = '';
    })
    addTransferClicked(document.querySelector('.hotel-search-container'));
}
function onlyTourClicked(e){
    document.querySelectorAll('.hotel-search-container').forEach(hotel => {
        hotel.innerHTML = '';
    })
    document.querySelectorAll('.transfer-search-container').forEach(hotel => {
        hotel.innerHTML = '';
    })
    addTourClicked(document.querySelector('.hotel-search-container'));
}