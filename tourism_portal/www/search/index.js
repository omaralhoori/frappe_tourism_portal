var availabeRooms = {}

$(document).ready(function(){
    updateAvailableRooms();
    checkRightSelected()
    lastCheckForButton();
})

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

function roomSelected(e) {
    e.querySelector('input[type="radio"]').click()
    // checkSelectedRoomsCount(e);
    updateAvailableRooms ();
}

function checkSelectedRoomsCount(e){
    console.log(e.parentNode.parentNode.parentNode)
}

function toggleUnselectedRoomAskButton(){
    if (value){
        
    }else{

    }
}