var totals = {
    "hotels": 0,
    "transfers": 0,
    "tours": 0
}
var reservation_details = {
    hotel: null
}
var availabeRooms = {}

$(document).ready(function(){
    toggleLoadingIndicator(true);
    // check if there is common rooms
    var results = checkCommonRooms(searchResults);
    formatResults(results);
    // updateAvailableRooms();
    // checkRightSelected()
    // lastCheckForButton();
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
            
            
            var resultFormatted = formatHotelResults(results[hotel]);
            if (accordion){
                var resultItem = $('#hotel-room-results-template').html()
                resultItem = resultItem.replaceAll("{Hotel ID}", hotel)
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
            hotelReuslts = `<div><label>${resultLabel}</label> ${hotelReuslts}</div>`
        }
        allHotelResults += hotelReuslts
    }
    $('.search-results').html(allHotelResults);

}

function formatHotelResults(hotelResults){
    var roomResultsFormated = "";
    for(var roomResult of hotelResults){
        var resultFormatted = formatRoomResult(roomResult)
        //console.log(resultFormatted)
        roomResultsFormated +=`<div class="room-result-container pax-${roomResult.details.pax}" room-id="${roomResult.details.room_id}" pax="${roomResult.details.pax}">
            ${resultFormatted}
        </div>`
    }
    return roomResultsFormated;
}

function formatRoomResult(roomResult){
    console.log(roomResult)
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
        roomDetails = `<div class="room-details-item"><div class="badge badge-primary">${roomResult['results'][0]['hotel_cancellation_policy']}</div></div>`
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
    reservation_details['hotel']= hotel;

    disable_other_hotel_selects(hotel)

    calculate_total_hotel(hotel)
}

function disable_other_hotel_selects(hotel){
    var selects = document.querySelectorAll('.room-select-input');
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
    for (var res of searchResults){
        searchCount++;
        var searchLabel = `Search ${searchCount} Results`
        results[searchLabel] = {}
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
    console.log(e.parentNode.parentNode.parentNode)
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
    console.log(e)
}

function calculate_total_hotel(hotel){
    var total = 0;
    var all_selects = document.querySelectorAll(`select.room-select-input[hotel="${hotel}"]`)
    for (var selectInput of all_selects){
        total += Number( selectInput.value || 0) * Number(selectInput.getAttribute("room-price"))
    }
    $('.hotels-total').text(`${total.toFixed(2)} USD`)
    totals['hotels'] = total;
    update_totals();
}

function update_totals(){
    var total = 0;
    for (var tt in totals){
        total += totals[tt]
    }

    $('.grand-total-container').text(`${total.toFixed(2)} USD`)
}

function confirmButtonClicked(e){
    var all_rooms_selected = false;
    var selected_rooms = {};
    // check if all rooms are selected
    var all_selects= document.querySelectorAll(`select.room-select-input[hotel="${reservation_details['hotel']}"]`)
    for (var ss of all_selects){
        var rooms = ss.getAttribute("rooms");
        var price = ss.getAttribute("room-price");
        var contractId = ss.getAttribute("contract-id");
        var roomId = ss.closest('.room-result-container').getAttribute('room-id')
        var value = 0;
        if (ss.value && ss.value > 0){
            value = ss.value;
        }
        if (!selected_rooms[rooms]){
            selected_rooms[rooms] = {}  
        }
        if (!selected_rooms[rooms][roomId]){
            selected_rooms[rooms][roomId] = {
                "price": price,
                "qty": 0,
                "contractId": contractId
            } 
        }

        selected_rooms[rooms][roomId]['qty'] += Number(value);
    }
    console.log(selected_rooms)

    if (Object.keys(selected_rooms).length == 0){
        all_rooms_selected = false;
    }else{
        all_rooms_selected = true;
        for (var room in selected_rooms){
            var roomCnt = room.split('-').length
            var selected = 0;
            for (var ss in selected_rooms[room]){
                var cc = selected_rooms[room][ss]['qty']
                selected += cc
            }
            if (selected != roomCnt){
                all_rooms_selected = false
            }
        }
    }
     if (!all_rooms_selected){
        msgprint("Please select all rooms")
     }else{
        
        selected_rooms['hotel'] = reservation_details['hotel'];
        var hotelParams = JSON.stringify(selected_rooms)
        var data = encodeParamsJson(selected_rooms)
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

}

function encodeParamsJson(selected_rooms){
    // ToDo Make encode for multiple hotels
    var searchParams = new URLSearchParams(window.location.search)
    var params = JSON.parse(searchParams.get("params"))
    var rooms = [];
    for (var room in selected_rooms){
        var roomNames = room.split('-')
        for (var ss in selected_rooms[room]){
            var selectedIndexes = 0;
            for (var i=0; i<selected_rooms[room][ss]['qty']; i++){
                var paxInfo = params[0]['paxInfo'].find(obj => obj.roomName == roomNames[selectedIndexes])
                var encodedRoom = {
                    "room_name": roomNames[selectedIndexes],
                    "room_id": ss,
                    "price": selected_rooms[room][ss]['price'],
                    "contract_id": selected_rooms[room][ss]['contractId'],
                    "pax_info": paxInfo,
                    "check_in": params[0]['checkin'],
                    "check_out": params[0]['checkout'],
                    "nationality": params[0]['nationality'],
                }
                rooms.push(encodedRoom)
                selectedIndexes++;
            }
        }
    }
    return {"rooms": rooms};
}