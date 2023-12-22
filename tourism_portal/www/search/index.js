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
    toggleLoadingIndicator(false);
})

function formatResults(allResults){
    var multipleResults = Object.keys(allResults).length > 1;
    var allHotelResults = "";
    for (var resultLabel in allResults){
        var results = allResults[resultLabel]
        var hotelReuslts = "";
        var accordion = Object.keys(results).length > 1;
        for (var hotel in results){
            // console.log(results[hotel])
            
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
        if (accordion){
            hotelReuslts = `<div id="accordion"> ${hotelReuslts}</div>`
        }
        if (multipleResults){
            hotelReuslts = `<div class="card p-3 mt-3" >${resultLabel}</div> ${hotelReuslts}`
        }
        hotelReuslts = `<div class='hotel-search-results' hotel-result="${resultLabel}"> ${hotelReuslts}</div>`
        allHotelResults += hotelReuslts
        reservation_details['hotel'][resultLabel] = null;
    }
    $('.search-results').html(allHotelResults);

}

function formatHotelResults(hotelResults){
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
        selectRoom = `<select 
        room-price="${roomResult['results'][0]['price'][0]}"
        onchange="roomSelectChanged(this)"  class="room-select-input"
        contract-id="${roomResult['results'][0]['contract_id']}"
        price-id="${roomResult['results'][0]['price'][3]}"
        hotel=${roomResult['results'][0]['hotel_id']} rooms="${rooms}">
        <option>0</option>
            ${selectRoom}
        </select>`
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
    return results
}

function compareRoomDetails(room1, room2){
    if (room1.price != room2.price) return false;
    if (room1.room_id != room2.room_id) return false;
    if (room1.pax != room2.pax) return false;
    return true;
}

function getRoomDetails(room){
    console.log(room)
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
            for (var tourItem of tourResult.querySelectorAll('.tour-item')){
                tours.push(tourItem.getAttribute('tour-id'))
            }
            selectedTours[tourSearchName].push({
                "tours": tours,
                "price": tourPrice,
                "pickup": tourPickup
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