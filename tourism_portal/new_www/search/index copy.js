var totals = {
    "hotels": 0,
    "transfers": 0,
    "tours": 0
}
var reservation_details = {
    hotel: {}
}
var availabeRooms = {}

$(document).ready(async function(){
    toggleLoadingIndicator(true);
    // check if there is common rooms
    var searchParams = new URLSearchParams(window.location.search)
    var res = await frappe.call({
        "method": "tourism_portal.api.search.get_search_results", 
        args: {"search": searchParams.get("search")},
    })
    if (res.message){
        searchResults = JSON.parse(res.message);
    }
    var results = checkCommonRooms(searchResults);
    formatResults(results);
    // updateAvailableRooms();
    // checkRightSelected()
    // lastCheckForButton();
    calculate_total_transfers()
    calculate_total_tours()
    autocompleteLocations(document.querySelector('.hotel-location'), 'tourism_portal.api.query.get_locations');
    autocompleteLocations(document.querySelector('.transfer-pickup-1'), 'tourism_portal.api.query.get_transfer_locations', (element) => {
        checkRegularFlights(element, 'arrival')
    });
    autocompleteLocations(document.querySelector('.transfer-pickup-2'), 'tourism_portal.api.query.get_transfer_locations',(element) => {
        checkRegularFlights(element, 'arrival')
    });
    autocompleteLocations(document.querySelector('.transfer-dropoff-1'), 'tourism_portal.api.query.get_transfer_locations',(element) => {
        checkRegularFlights(element, 'departure')
    });
    autocompleteLocations(document.querySelector('.transfer-dropoff-2'), 'tourism_portal.api.query.get_transfer_locations',(element) => {
        checkRegularFlights(element, 'departure')
    });

    formatSelect2()
    formatDataPicker()
    toggleLoadingIndicator(false);
})

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

function formatResults(allResults){
    var multipleResults = Object.keys(allResults).length > 1;
    var allHotelResults = "";
    for (var resultLabel in allResults){
        var results = allResults[resultLabel]
        var hotelReuslts = "";
        var accordion = Object.keys(results).length > 1;
        for (var hotel in results){
            
            var resultFormatted = formatHotelResults(results[hotel]);
            if (accordion){
                var resultItem = $('#hotel-room-results-template').html()
                var location  = '';
                if (results[hotel][0]['results'][0]['gps_location']){
                    location = `<a target="_blank" href="https://maps.google.com/?q=${results[hotel][0]['results'][0]['gps_location']}" >Location On Map</a>`
                }
                var minPrice = null;
                for (var room of results[hotel]){
                    if (room.details.price){
                        if (!minPrice){
                            minPrice = room.details.price;
                        }else{
                            if (room.details.price < minPrice){
                                minPrice = room.details.price;
                            }
                        }

                    }
                }
                resultItem = resultItem.
                    replaceAll("{Hotel ID}", hotel).
                    replaceAll("{Hotel Name}", results[hotel][0]['results'][0]['hotel_name']).
                    replaceAll("{Hotel Image}", results[hotel][0]['results'][0]['hotel_image'] || '/assets/tourism_portal/images/no-image.jpg').
                    replaceAll("{Hotel Location}", location).
                    replaceAll("{Hotel Stars}", results[hotel][0]['results'][0]['star_rating'] || '').
                    replaceAll("{Hotel Address}", results[hotel][0]['results'][0]['address'] || '').
                    replaceAll("{Hotel Price}", minPrice? minPrice.toFixed(2) : 'N/A');
                var $resultItem = $(resultItem);
                $resultItem.find('.card-body').html(`<div class="hotel-cards" hotel-id="${hotel}">${resultFormatted}</div>`)
                resultItem = $resultItem.prop('outerHTML');
                hotelReuslts += resultItem
            }else{
                hotelReuslts += `<div class="hotel-cards" hotel-id="${hotel}">${resultFormatted}</div>`
            }
           
        }
        // if (accordion){
        //     hotelReuslts = `<div id="accordion"> ${hotelReuslts}</div>`
        // }
        //if (multipleResults){
            hotelReuslts = `<div class="card p-3 mt-3" >${renderHotelSearchBar(resultLabel, accordion)}</div> ${hotelReuslts}`
        //}
        hotelReuslts = `<div class='hotel-search-results' hotel-result="${resultLabel}"> ${hotelReuslts}</div>`
        allHotelResults += hotelReuslts
        reservation_details['hotel'][resultLabel] = null;
    }
    $('.search-results').html(allHotelResults);

}

function hotelSearchStarChanged(e){
    var selected = e.value;
    e.closest(".hotel-search-results").querySelectorAll(`div.hotel-stars`).forEach(hotel => {
            hotel.closest('.hotel-card').style.display="block";
        })
    if (!selected || selected ==""){
    }else{
        var hotels = e.closest(".hotel-search-results").querySelectorAll(`div.hotel-stars:not([star-rating='${selected}'])`)
        hotels.forEach(hotel => {
            hotel.closest('.hotel-card').style.display="none";
        })

    }
}

function renderHotelSearchBar(resultLabel, multipleResults){
    var filters = ""
    if (multipleResults){
        filters += `
            <select class="form-select" onchange="hotelSearchStarChanged(this)">
            <option value ="" selected>Star Rating</option>
            <option value="One Star">One Star</option>
            <option value="Two-Star">Two-Star</option>
            <option value="Three-Star">Three-Star</option>
            <option value="Four-Star">Four-Star</option>
            <option value="Five-Star">Five-Star</option>
            </select>
        `
    }
    var html = `
        <div class="d-flex justify-content-between">
            <div class="hotel-search-label">${resultLabel}</div>

            <div class="hotel-search-buttons d-flex">
                <div class="search-filters mr-2">
                ${filters}
                </div>
                <button class="btn btn-sm" search-results="${resultLabel}"
                 onclick="editHotelSearchResults(this)">Edit <i class="fa fa-pencil"></i></button>
            </div>
        </div>
    `;

    return html;
}

function editHotelSearchResults(e){
    var searchResults = e.getAttribute('search-results');
    var $modal = $('#hotelSearchModal');
    var hotelParams = hotelSearchParams[searchResults];

    $locationInput = $modal.find('input[name="location"]')
    $locationInput.val(hotelParams['location-name'])
    $locationInput.attr('location-id', hotelParams['location'])
    $locationInput.attr('location-name', hotelParams['location-name'])
    $locationInput.attr('location-type', hotelParams['location-type'])

    $modal.find('input[name="check-in"]').val(hotelParams['checkin'])
    $modal.find('input[name="check-out"]').val(hotelParams['checkout'])
    $modal.find('select[name="nationality"]').val(hotelParams['nationality'])

    $modal.find('select[name="room"]').val( hotelParams['room']).change();
    $modal.find(`.pax-search-card`).each(function(i, card){
        var pax = hotelParams['paxInfo'][i]
        $(card).find(`select[name="adult"]`).val(pax['adults'] || "0").change()
        $(card).find(`select[name="children"]`).val(pax['children'] || "0").change()
        var ages = pax['childrenInfo'] || []
        for (var j=0; j<ages.length; j++){

            $(card).find(`select[name="child-age"]`).eq(j).val(ages[j])
        }
    })

    $modal.find('.modal-title').text(`Edit ${searchResults} Search`);
    $modal.find('input[name="hotel-card"]').val(searchResults);
    $modal.modal('show');
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

function editTransferSearchResults(e){
    var searchResults = e.getAttribute('search-results');
    var $modal = $('#transferSearchModal');
    $modal.find('input[name="transfer-card"]').val(searchResults);
    var transferParams = transferSearchParams[searchResults];
    var twoWay = Object.keys(transferParams).length > 1;
    var transferRows = {
        0: "departure-transfer",
        1: "return-transfer"
    }
    var transferRoutes = {
        0: "arrival",
        1: "departure"
    }
    for (var transferRoute in transferParams){
        var transferRouteParams = transferParams[transferRoute];
        var $transferRow = $modal.find(`.${transferRows[transferRoute]}`)
        var $pickupLocation = $transferRow.find('input[name="pickup"]')
        $pickupLocation.val(transferRouteParams['from-location-name'])
        $pickupLocation.attr('location-id', transferRouteParams['from-location'])
        $pickupLocation.attr('location-name', transferRouteParams['from-location-name'])
        $pickupLocation.attr('location-type', transferRouteParams['from-location-type'])
        $dropoffLocation = $transferRow.find('input[name="dropoff"]')
        $dropoffLocation.val(transferRouteParams['to-location-name'])
        $dropoffLocation.attr('location-id', transferRouteParams['to-location'])
        $dropoffLocation.attr('location-name', transferRouteParams['to-location-name'])
        $dropoffLocation.attr('location-type', transferRouteParams['to-location-type'])
        $transferRow.find('input[name="check-in"]').val(transferRouteParams['transfer-date'])
        $transferRow.find('select[name="transfer-type"]').val(transferRouteParams['transfer-type'])
        $transferRow.find('input[name="flight-no"]').val(transferRouteParams['flight-no'])
        $transferRow.find('select[name="adult"]').val(transferRouteParams['paxes']['adults'])
        $transferRow.find('select[name="children"]').val(transferRouteParams['paxes']['children']).change()
        var ages = transferRouteParams['paxes']['child-ages'] || []
        for (var j=0; j<ages.length; j++){
            $transferRow.find(`select[name="child-age"]`).eq(j).val(ages[j])
        }
        checkRegularFlights($pickupLocation[0].parentNode, 'arrival')
        checkRegularFlights($dropoffLocation[0].parentNode, 'departure')

    }

    if (!twoWay){
        var routeBtn = $modal.find('.route-btn')
        $modal.find('.return-transfer').addClass('d-none');
        routeBtn.attr("data-way", "two-way")
        routeBtn.html(`<i class="fa fa-exchange" aria-hidden="true"></i> Two Way`)
    }

    $modal.find('.modal-title').text(`Edit ${searchResults}`);
    $modal.find('input[name="hotel-card"]').val(searchResults);
    $modal.modal('show');
}
function sortHotelResults(a, b) {
    if (a.details.price === null && b.details.price === null) {
      return 0; // Both have null prices, leave them in their current order
    } else if (a.details.price === null) {
      return 1; // Null comes after non-null
    } else if (b.details.price === null) {
      return -1; // Non-null comes before null
    } else {
      return a.details.price - b.details.price; // Sort based on price
    }
  }
function formatHotelResults(hotelResults){
    hotelResults.sort(sortHotelResults)
    var roomResultsFormated = "";
    for(var roomResult of hotelResults){
        var resultFormatted = formatRoomResult(roomResult)
        roomResultsFormated +=`<div class="room-result-container pax-${roomResult.details.pax}" room-id="${roomResult.details.room_id}" pax="${roomResult.details.pax}">
            ${resultFormatted}
        </div>`
    }
    return roomResultsFormated;
}

function formatRoomResult(roomResult){
    var resultItem = $('#room-result-item-template').html()
    var showAskButton = false;
    if (!roomResult.details.price){
        resultItem = $(resultItem)
            .find('.room-price-container')
            .remove()
            .end()
            .prop('outerHTML');
        showAskButton = true;
    }else{
        resultItem= resultItem
        .replace('{Room Price}', parseFloat(roomResult['results'][0]['price'][0]).toFixed(2))
        .replace('{Nights}', roomResult['results'][0]['price'][1])
    }

    var roomDetails = ''
    if (roomResult['results'][0]['hotel_cancellation_policy']){
        roomDetails = `<div class="room-details-item pop-container">
        <div class="badge badge-primary ">
            ${roomResult['results'][0]['hotel_cancellation_policy']}
        </div>
        <div class="pop-details">${roomResult['results'][0]['cancellation_policy_description']}</div>
    </div>`
    }
    if (roomResult['results'][0]['features']){
        for (var dd of roomResult['results'][0]['features'])
            roomDetails += `<div class="room-details-item">${dd}</div>`
    }

    resultItem = $(resultItem)
            .find('.room-details')
            .html(roomDetails)
            .end()
            .prop('outerHTML');
    
    if (roomResult['results'][0]['room_image']){
        resultItem= resultItem
        .replace('{Room Image}', roomResult['results'][0]['room_image']) 
    }else{
        resultItem= resultItem
        .replace('{Room Image}', '/assets/tourism_portal/images/no-image.jpg') 
    }
    if (roomResult.results[0]['qty'] < 1){
        showAskButton = true;
    }
    var showAvailableLabel = roomResult.results[0]['qty'] < roomResult['rooms'].length + 2
    if (!showAvailableLabel){
        resultItem = $(resultItem)
    .find('.room-available-label')
    .remove()
    .end()
    .prop('outerHTML');
    }
    if (!showAskButton){
        var selectRoom = ``; 
        var rooms = roomResult['rooms'].join('-')
        for (var room in roomResult['rooms']){
            var roomNo = Number(room) + 1
            if (roomNo <= Number(roomResult.results[0]['qty'])){
                selectRoom += `<option value="${roomNo}">${roomNo}</option>`
            }
            
        }
        selectRoom = `<div><label>Rooms: </label> <select 
        room-price="${roomResult['results'][0]['price'][0]}"
        onchange="roomSelectChanged(this)"  class="room-select-input"
        contract-id="${roomResult['results'][0]['contract_id']}"
        price-id="${roomResult['results'][0]['price'][3]}"
        hotel=${roomResult['results'][0]['hotel_id']} rooms="${rooms}">
        <option>0</option>
            ${selectRoom}
        </select></div>`
        resultItem = $(resultItem)
        .find('.ask-button-container')
        .after(selectRoom)
        .remove()
        .end()
        .prop('outerHTML');

        
    }
    var modified = resultItem
                .replace('{Hotel Name}', roomResult['results'][0]['hotel_name'])
                .replace('{Room Type}', roomResult['results'][0]['room_type'])
                .replace('{Available QTY}', `Avilable ${roomResult['results'][0]['qty']}`)
                .replace('{PAX IMAGE}', `/assets/tourism_portal/images/pax/${roomResult.details.pax}.png`);
    
    return modified;
}

function roomSelectChanged(e){
    var rooms = e.getAttribute("rooms")
    var hotel = e.getAttribute("hotel")
    var hotel_search =e.closest('.hotel-search-results').getAttribute('hotel-result')
    var selectedRooms = 0;
    var requiredRoomsToSelect = rooms.split('-').length
    // get other selects with same rooms
    var roomSelects = document.querySelectorAll(`select[rooms='${rooms}'][hotel='${hotel}']`)
    for (var ss of roomSelects){
        selectedRooms += Number(ss.value || 0)
    }
    // disable all options remainings
    requiredRoomsToSelect = requiredRoomsToSelect - selectedRooms
    for (var ss of roomSelects){
        for (var option of ss.options){
            if (option.value > requiredRoomsToSelect){
                option.disabled = true;
            }else{
                option.disabled = false;
            }
        }
    }
    reservation_details['hotel'][hotel_search]= hotel;

    disable_other_hotel_selects(hotel, hotel_search)

    calculate_total_hotel(hotel, hotel_search)
}

function disable_other_hotel_selects(hotel, hotel_search){
    var selects = document.querySelectorAll(`.hotel-search-results[hotel-result="${hotel_search}"] .room-select-input`);
    for (var select of selects){
        if (select.getAttribute('hotel') == hotel){
            continue;
        }else{
            select.value = "0";
        }
    }
}

function checkCommonRooms(searchResults){
    console.log(searchResults)
    var results = {}
    var searchCount = 0;
    for (var resultName in searchResults){
        searchCount++;
        var searchLabel = resultName//`Search ${searchCount} Results`
        results[searchLabel] = {}
        var res = searchResults[resultName];
        for (var hotel in res){
            results[searchLabel][hotel] = []
            for (var roomResults in res[hotel]) {
                for (var room of res[hotel][roomResults]){
                    var found = false;
                    var roomDetails = getRoomDetails(room)
                    for (var commonRoom of results[searchLabel][hotel]){
                        if (compareRoomDetails(commonRoom.details,  roomDetails)){
                            found = true;
                            commonRoom.rooms.push(roomResults)
                            commonRoom.results.push(room)
                            break;
                        }
                    }
                    if (!found){
                        results[searchLabel][hotel].push({
                            "rooms": [roomResults],
                            "details": roomDetails,
                            "results": [room]
                        })
                    }
                }
               
            }
        }
        
    }
    console.log(results)
    return results
}

function compareRoomDetails(room1, room2){
    if (room1.price != room2.price) return false;
    if (room1.room_id != room2.room_id) return false;
    if (room1.pax != room2.pax) return false;
    return true;
}

function getRoomDetails(room){

    var details = {
        "price": room['price'] ? room['price'][0] : null,
        "room_id": room['room_id'],
        "pax": room['pax']['adults'] + "-" + room['pax']['children'],
    }
    return details;
}

function lastCheckForButton(){
    for (var contractId in availabeRooms){
        var selectedQty = availabeRooms[contractId][0] - availabeRooms[contractId][1]
        var rooms = document.querySelectorAll(`.room-result-item input[contract-id="${contractId}"]`);
        while (selectedQty < 0){
            
        }
    }
}

function updateAvailableRooms () {
    availabeRooms = {}
    var allRooms = document.querySelectorAll(".room-result-item input[type='radio']")
    for (var room of allRooms ){
        var contractId = room.getAttribute("contract-id")
        var qty = room.getAttribute("room-qty")
        var selected = room.checked  
        if (! availabeRooms[contractId]){
            availabeRooms[contractId] = [qty, 0]
        }
            if(selected)
            availabeRooms[contractId][1] = availabeRooms[contractId][1] + 1;

    }
    updateAvailableLabels()
}

function updateAvailableLabels(){
    var allRooms = document.querySelectorAll(".room-result-item input[type='radio']")
    for (var room of allRooms ){
        var contractId = room.getAttribute("contract-id")
        var selected = room.checked  
        var availables = availabeRooms[contractId][0] - availabeRooms[contractId][1]
        availables=availables < 1 ? 0 : availables; 
        room.parentNode.querySelector('.room-available-label').innerText = 'Available ' +   availables
        if(!selected && availables < 1)
            room.parentNode.querySelector('.ask-button-container').style.display = 'block';
        else if (availables > 0){
            room.parentNode.querySelector('.ask-button-container').style.display = 'none';
        }
    }
}

function checkRightSelected(){
    for (var contractId in availabeRooms){
        var selectedQty = availabeRooms[contractId][0] - availabeRooms[contractId][1]
        if (selectedQty < 0){
            var allRooms = document.querySelectorAll(`.room-result-item input[contract-id="${contractId}"]`);
            for(var i = allRooms.length-1; i>=0 && selectedQty < 0; i--){
                var room = allRooms[i]
            var parentNode = room.parentNode.parentNode.parentNode.parentNode;
            while(true){
                var sibiling = parentNode.nextElementSibling
                parentNode = sibiling;
                if (! sibiling){
                    break;
                }
                if (checkAvailableNode(sibiling)){
                    selectedQty ++;
                    break;
                }
            }
            }
            
        }
    }
}

function checkAvailableNode(node){
    var element = node.querySelector("input[type='radio']")
    var contractId=element.getAttribute("contract-id");
    if (! contractId ) return false;
    var avlbl =  availabeRooms[contractId][0] - availabeRooms[contractId][1];
    if(avlbl < 1) return false;
    element.click();
    updateAvailableRooms();
    return true
}

// function roomSelected(e) {
//     e.querySelector('input[type="radio"]').click()
//     // checkSelectedRoomsCount(e);
//     updateAvailableRooms ();
// }

function checkSelectedRoomsCount(e){
}

function toggleUnselectedRoomAskButton(){
    if (value){
        
    }else{

    }
}

function askButtonClicked(e){
    var roomId = $(e).closest('.room-result-container').attr('room-id');
    frappe.call({
        "method": "tourism_portal.www.search.index.ask_for_availability",
        args: {
            room_id: roomId,
        },
        callback: res => {
            if (res.message ){
                if (res.message.success_key == 1 && res.message.msg){
                    msgprint(res.message.msg, "Message")
                }else if  (res.message.success_key == 0 && res.message.error){
                    msgprint(res.message.error, "Error")
                }
            }
        }
    })
}

function calculate_total_hotel(hotel, hotel_search){
    var total = 0;
    var all_selects =document.querySelectorAll(`.hotel-search-results select.room-select-input`); //document.querySelectorAll(`.hotel-search-results[hotel-result="${hotel_search}"] select.room-select-input[hotel="${hotel}"]`)
    for (var selectInput of all_selects){
        total += Number( selectInput.value || 0) * Number(selectInput.getAttribute("room-price"))
    }
    $('.hotels-total').text(`${total.toFixed(2)} USD`)
    totals['hotels'] = total;
    update_totals();
}

function calculate_total_transfers(){
    var total = 0;
    var all_selects = document.querySelectorAll(`.transfer-price`)
    for (var selectInput of all_selects){
        total += Number(selectInput.getAttribute("transfer-price"))
    }
    $('.transfers-total').text(`${total.toFixed(2)} USD`)
    totals['transfers'] = total;
    update_totals();
}

function calculate_total_tours(){
    var total = 0;
    var all_selects = document.querySelectorAll(`.tour-price`)
    for (var selectInput of all_selects){
        total += Number(selectInput.getAttribute("tour-price"))
    }
    $('.tours-total').text(`${total.toFixed(2)} USD`)
    totals['tours'] = total;
    update_totals();
}

function update_totals(){
    var total = 0;
    for (var tt in totals){
        total += totals[tt]
    }

    $('.grand-total-container').text(`${total.toFixed(2)} USD`)
}
function getSelectedRooms(){
    var selected_rooms = {};
    var all_rooms_selected = false;
    for (var hotelSearch in reservation_details['hotel']){
       
        selected_rooms[hotelSearch] = {};
        // check if all rooms are selected
        var all_selects= document.querySelectorAll(`div[hotel-result="${hotelSearch}"] select.room-select-input[hotel="${reservation_details['hotel'][hotelSearch]}"]`)
        for (var ss of all_selects){
            var rooms = ss.getAttribute("rooms");
            var price = ss.getAttribute("room-price");
            var contractId = ss.getAttribute("contract-id");
            var priceId = ss.getAttribute("price-id");
            var roomId = ss.closest('.room-result-container').getAttribute('room-id')
            var value = 0;
            if (ss.value && ss.value > 0){
                value = ss.value;
            }
            if (!selected_rooms[hotelSearch][rooms]){
                selected_rooms[hotelSearch][rooms] = {}  
            }
            if (!selected_rooms[hotelSearch][rooms][roomId]){
                selected_rooms[hotelSearch][rooms][roomId] = {
                    "price": price,
                    "qty": 0,
                    "contractId": contractId,
                    "priceId": priceId
                } 
            }
    
            selected_rooms[hotelSearch][rooms][roomId]['qty'] += Number(value);
        }
    
        if (Object.keys(selected_rooms[hotelSearch]).length == 0){
            all_rooms_selected = false;
            break;
        }else{
            all_rooms_selected = true;
            for (var room in selected_rooms[hotelSearch]){
                var roomCnt = room.split('-').length
                var selected = 0;
                for (var ss in selected_rooms[hotelSearch][room]){
                    var cc = selected_rooms[hotelSearch][room][ss]['qty']
                    selected += cc
                }
                if (selected != roomCnt){
                    all_rooms_selected = false
                    break
                }
            }
            if (!all_rooms_selected){
                break;
            }
        }
    }
    if (!all_rooms_selected && Object.keys(reservation_details['hotel']).length > 0){
        msgprint("Please select all rooms")
        return false;
     }else{
        for(var hotelSearch in reservation_details['hotel']){
            selected_rooms[hotelSearch]['hotel'] = reservation_details['hotel'][hotelSearch];
        }
        return selected_rooms;
     }
}

function getSelectedTransfers(){   
    var selectedTransfers = {};
    var all_transfer_searchs = document.querySelectorAll('.transfer-search')
    for (var transferSearch of all_transfer_searchs){
        var transferSearchName = transferSearch.getAttribute('transfer-search')
        selectedTransfers[transferSearchName] = {};
        var transferResults = transferSearch.querySelectorAll('.transfer-card')
        for (var transferResult of transferResults){
            var transferName = transferResult.getAttribute('transfer-name')
            selectedTransfers[transferSearchName][transferName] = {
                "transfer_id": transferResult.getAttribute('transfer-type'),
                "transfer_price": transferResult.getAttribute('transfer-price'),
                "pick_up_postal_code": transferResult.getAttribute('from-postal-code'),
                "drop_off_postal_code": transferResult.getAttribute('to-postal-code'),
                "flight_no": transferResult.getAttribute('flight-no'),
            }
            // selectedTransfers[transferSearchName].push(transferId)
        }
    }
    return selectedTransfers
}

function getSelectedTours(){
    var selectedTours = {};
    var all_tour_searchs = document.querySelectorAll('.tour-search-card')
    for (var tourSearch of all_tour_searchs){
        var tourSearchName = tourSearch.getAttribute('tour-search')
        selectedTours[tourSearchName] = [];
        var tourResults = tourSearch.querySelectorAll('.tour-card')
        for (var tourResult of tourResults){
            var tourPrice = tourResult.querySelector('.tour-price').getAttribute('tour-price')
            var tourPickup = tourResult.querySelector('.tour-pickup').getAttribute('tour-pickup')
            var tours = []
            var toursPrice = {}
            for (var tourItem of tourResult.querySelectorAll('.tour-item')){
                tours.push(tourItem.getAttribute('tour-id'))
                toursPrice[tourItem.getAttribute('tour-id')] = tourItem.getAttribute('tour-indv-price')
            }
            selectedTours[tourSearchName].push({
                "tours": tours,
                "price": tourPrice,
                "pickup": tourPickup,
                "toursPrice": toursPrice
            })
        }
    }


    return selectedTours;
}

function confirmButtonClicked(e){
    var selected_rooms = getSelectedRooms();
   if (!selected_rooms){
    return
   }
   var selected_transfers = getSelectedTransfers();
   var selected_tours = getSelectedTours();
    var data = encodeParamsJson(selected_rooms, selected_transfers, selected_tours)
    var url = "tourism_portal.api.reserve.create_reservation"
    toggleLoadingIndicator(true);
    frappe.call({
        "method": url,
        args: data,
        callback: res => {
            if (res.message){
                window.location.href = `/reserve?invoice=${res.message}`
            }else{
                toggleLoadingIndicator(false);
                // ToDo show Error message
            }
        }
    })
    

}

function encodeParamsJson(selected_rooms, selected_transfers, selected_tours){
    // ToDo Make encode for multiple hotels
    // var searchParams = new URLSearchParams(window.location.search)
    // var params = JSON.parse(searchParams.get("params"))
    
    var hotelParams = hotelSearchParams//params['hotelParams']
    var transferParams = transferSearchParams//params['transferParams']
    var tourParams = tourSearchParams//params['toursparams']
    var room_search = encodeHotelRoomSeearch(hotelParams, selected_rooms);
    var tour_search = encodeTourSearch(tourParams, selected_tours);
    var transfer_search = encodeTransferSearch(transferParams, selected_transfers);
    return {"rooms": room_search, "transfers": transfer_search, "tours": tour_search};
}

function encodeTransferSearch(transferParams, selected_transfers){
    var all_selected = {}
    for (var cardName in selected_transfers){
        all_selected[cardName] = {}
        for (var searchName in selected_transfers[cardName]){
            all_selected[cardName][searchName] = {}
            all_selected[cardName][searchName]['transfer_type'] = transferParams[cardName][searchName]['transfer-type'];
            all_selected[cardName][searchName]['pick_up'] = transferParams[cardName][searchName]['from-location'];
            all_selected[cardName][searchName]['drop_off'] = transferParams[cardName][searchName]['to-location'];
            all_selected[cardName][searchName]['pick_up_type'] = transferParams[cardName][searchName]['from-location-type'];
            all_selected[cardName][searchName]['drop_off_type'] = transferParams[cardName][searchName]['to-location-type'];
            all_selected[cardName][searchName]['transfer_date'] = transferParams[cardName][searchName]['transfer-date'];
            all_selected[cardName][searchName]['pax_info'] = {};
            all_selected[cardName][searchName]['pax_info']['adults'] = transferParams[cardName][searchName]['paxes']['adults'];
            all_selected[cardName][searchName]['pax_info']['children'] = transferParams[cardName][searchName]['paxes']['children'];
            all_selected[cardName][searchName]['pax_info']['childrenInfo'] = transferParams[cardName][searchName]['paxes']['child-ages'];
            all_selected[cardName][searchName]['transfer_id'] = selected_transfers[cardName][searchName]['transfer_id'];
            all_selected[cardName][searchName]['transfer_price'] = selected_transfers[cardName][searchName]['transfer_price'];
            all_selected[cardName][searchName]['pick_up_postal_code'] = selected_transfers[cardName][searchName]['pick_up_postal_code'];
            all_selected[cardName][searchName]['drop_off_postal_code'] = selected_transfers[cardName][searchName]['drop_off_postal_code'];
            all_selected[cardName][searchName]['flight_no'] = selected_transfers[cardName][searchName]['flight_no'];
        }
    }
    return all_selected
}

function encodeHotelRoomSeearch(hotelParams, selected_rooms){
    var all_searches = {}
    for (search in selected_rooms){
        var rooms = {};
        for (var room in selected_rooms[search]){
            var roomNames = room.split('-')
            for (var ss in selected_rooms[search][room]){
                var selectedIndexes = 0;
                for (var i=0; i<selected_rooms[search][room][ss]['qty']; i++){
                    var paxInfo = hotelParams[search]['paxInfo'].find(obj => obj.roomName == roomNames[selectedIndexes])
                    var encodedRoom = {
                        "search_name": search,
                        "room_name": roomNames[selectedIndexes],
                        "room_id": ss,
                        "price": selected_rooms[search][room][ss]['price'],
                        "contract_id": selected_rooms[search][room][ss]['contractId'],
                        "pax_info": paxInfo,
                        "check_in": hotelParams[search]['checkin'],
                        "check_out": hotelParams[search]['checkout'],
                        "nationality": hotelParams[search]['nationality'],
                    }
                    // ToDo Add multiple contracts
                    // Add Price id
                    if (selected_rooms[search][room][ss]['contractId']){
                        encodedRoom['contracts'] = []
                        encodedRoom['contracts'].push({
                            "contract_id": selected_rooms[search][room][ss]['contractId'],
                            "price_id": selected_rooms[search][room][ss]['priceId'],
                            "price": selected_rooms[search][room][ss]['price'],
                            "check_in": hotelParams[search]['checkin'],
                            "check_out": hotelParams[search]['checkout'],
                        })
                    }
                    rooms[roomNames[selectedIndexes]] = encodedRoom
                    selectedIndexes++;
                }
            }
        }
        all_searches[search] = rooms;
    }
    return all_searches;
}
function encodeTourSearch(tourParams, selected_tours){
    var all_selected = {}
    for (var searchName in selected_tours){
        var paxes = tourParams[searchName]['paxes']
        all_selected[searchName] = {
            "pickup": tourParams[searchName]['location'],
            "pickup_type": tourParams[searchName]['location-type'],
            "check_in": tourParams[searchName]['checkin'],
            "check_out": tourParams[searchName]['checkout'],
            "tour_type": tourParams[searchName]['tour-type'],
            "paxes": paxes,
            "selected_tours": selected_tours[searchName]
        }

    }
    return all_selected
}
// window.addEventListener('beforeunload', function() {
//    frappe.call({
//     "method": "tourism_portal.api.reserve.delete_reservation",
// args:{"invoice": "TX-----ss"},
//     callback: res => {
//         if (res.message){
//         }
//     }
//    })
//   });

function seeHotelMoreDetails(e){
    var hotelCard = e.closest('.hotel-card');
    hotelCard.querySelector('.full-details').classList.toggle('d-none');
    hotelCard.querySelector('.short-details').classList.toggle('d-none');
    hotelCard.querySelector('.hotel-rooms-details').style.maxHeight = 'none';

}

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
function dropoffTransferChanged(e) {
    // checkRegularFlights(e, 'arrival');
}
function pickupTransferChanged(e) {
    // checkRegularFlights(e, 'arrival');
}

function newHotelSearchClicked(e){
    toggleLoadingIndicator(true);
    var searchCard = e.closest('.modal-content').querySelector('.hotel-new-search-card')
    var hotelSearch = searchCard.querySelector('input[name="hotel-card"]').value;
    var newParams = getHotelSearchInfo(searchCard, true);
    var searchParams = new URLSearchParams(window.location.search);
    hotelSearchParams[hotelSearch] = newParams;
    frappe.call({
        method: "tourism_portal.api.search.set_new_search_results",
        args: {
            search: searchParams.get('search'),
            hotel_params: hotelSearchParams,
        },
        callback: res => {
            window.location.reload();
        }
    })

}
function newTransferSearchClicked(e){
    var searchCard = e.closest('.modal-content').querySelector('.transfer-search-card')

    var transferSearch = searchCard.querySelector('input[name="transfer-card"]').value;
    var newParams = getTransferSearchInfo(searchCard, true);
    toggleLoadingIndicator(true);

    var searchParams = new URLSearchParams(window.location.search);
    transferSearchParams[transferSearch] = newParams;
    frappe.call({
        method: "tourism_portal.api.search.set_new_search_results",
        args: {
            search: searchParams.get('search'),
            transfer_params: transferSearchParams,
        },
        callback: res => {
            window.location.reload();
        }
    })

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

function transferTypeChanged(e) {
    if (e.value == 'group') {
        e.closest('form').querySelector('.allowed-flights').style.display = 'block';
    } else {
        e.closest('form').querySelector('.allowed-flights').style.display = 'none';
    }
}

function transferSelectedNewType(e){
    var selectedOption = e.options[e.selectedIndex];
    var transferCard = e.closest('.transfer-card');
    transferCard.querySelector('.card-title').innerText = selectedOption.getAttribute('transfer_type_name');
    transferCard.querySelector('.card-img-top').src = selectedOption.getAttribute('transfer_image');
    transferCard.querySelector('.transfer-description').innerText = selectedOption.getAttribute('transfer_description') || "";
    var priceContainer = transferCard.querySelector('.transfer-price')
    priceContainer.innerHTML = 'Price: ' + selectedOption.getAttribute('transfer_price');
    priceContainer.setAttribute('transfer-price', selectedOption.getAttribute('transfer_price'));
    transferCard.setAttribute('transfer-type', selectedOption.getAttribute('transfer_type_id'));
    transferCard.setAttribute('transfer-price', selectedOption.getAttribute('transfer_price'));
    calculate_total_transfers()
}