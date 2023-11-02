var totals = {
    "hotels": 0,
    "transfers": 0,
    "tours": 0
}
var availabeRooms = {}

$(document).ready(function(){
    toggleLoadingIndicator(true);
    // check if there is common rooms
    // console.log(searchResults)
    var results = checkCommonRooms(searchResults);
    formatResults(results);
    // updateAvailableRooms();
    // checkRightSelected()
    // lastCheckForButton();
    toggleLoadingIndicator(false);
})

function formatResults(results){
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
    $('.search-results').html(hotelReuslts);
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
        .replace('{Room Price}', roomResult['results'][0]['price'][0])
        .replace('{Nights}', roomResult['results'][0]['price'][1])
    }
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

    calculate_total_hotel(hotel)
}

function checkCommonRooms(searchResults){
    var results = {}
    for (var res of searchResults){
        for (var hotel in res){
            results[hotel] = []
            for (var roomResults in res[hotel]) {
                for (var room of res[hotel][roomResults]){
                    var found = false;
                    var roomDetails = getRoomDetails(room)
                    for (var commonRoom of results[hotel]){
                        if (compareRoomDetails(commonRoom.details,  roomDetails)){
                            found = true;
                            commonRoom.rooms.push(roomResults)
                            commonRoom.results.push(room)
                            break;
                        }
                    }
                    if (!found){
                        results[hotel].push({
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
    $('.hotels-total').text(`${total} USD`)
    totals['hotels'] = total;
    update_totals();
}

function update_totals(){
    var total = 0;
    for (var tt in totals){
        total += totals[tt]
    }

    $('.grand-total-container').text(`${total} USD`)
}