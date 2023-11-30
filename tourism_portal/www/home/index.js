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
    html += document.querySelector('.transfer-search-template').innerHTML;
    childrenContainer.innerHTML = html;
    e.style.display = 'none';
    
}
function addHotelClicked(e) {
    var container = $('.hotel-search-container');

     
    var html = '';
    var resultItem = $('#hotel-search-template').html()
    html += resultItem//document.querySelector('.hotel_search_template').innerHTML;
     // Add a new element next to the selected last element
    
     container.append(html);
     formatSelect2()
     
    // var html = '';
    // html += document.querySelector('.transfer-search-template').innerHTML;
    // childrenContainer.innerHTML = html;
    // e.style.display = 'none';
    
}

function searchBtnClicked(e){
    var hotelParams = getHotelParams();
    const paramsJSON = JSON.stringify(hotelParams);

    window.open(`search?params=${encodeURIComponent(paramsJSON)}`, '_self');

    // console.log(new URLSearchParams().toString());
}

function getHotelParams(){
    var hotelCards = document.querySelectorAll('.hotel-search-card');
    var hotelParams = []
    hotelCards.forEach(hotel => {
        hotelParams.push( getHotelSearchInfo(hotel))
    })
    return hotelParams;
}

function getHotelSearchInfo(hotel){
    var params = {};
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