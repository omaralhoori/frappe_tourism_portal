$(document).ready(function () {
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
});

function saveEdit(e){
    validateReservationData();
    var invoiceId = new URLSearchParams(window.location.search).get('invoice');
    var transfersInfo = getTransferInfo();
    var toursInfo = getToursInfo();
    console.log(transfersInfo)
    frappe.call({
        "method": "tourism_portal.api.reserve.update_reservation",
        "args": {
            "invoice_id": invoiceId,
            "transfers_info": transfersInfo,
            "tours_info": toursInfo,
        },
        "callback": function (r) {
            console.log(r)
            if (r.message){
                window.location.href = "/reserve?invoice=" + invoiceId;
            }
        }
    })
}

function cancelEdit(e){
    validateReservationData();
    var invoiceId = e.getAttribute("invoice-id");
    window.location.href = "/reserve?invoice=" + invoiceId;
}
function addTransfer(e){
    var invoiceId = e.getAttribute("invoice-id");
    var $modal = $('#transferSearchModal');
    $modal.find('.transfer-search-card').removeClass('d-none');
    $modal.find('.trasnfer_results').addClass('d-none');
    $modal.modal('show');
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

function newTransferSearchClicked(e){
    var searchCard = e.closest('.modal-content').querySelector('.transfer-search-card')

    var transferSearch = searchCard.querySelector('input[name="transfer-card"]').value;
    var newParams = getTransferSearchInfo(searchCard, true);
    toggleLoadingIndicator(true);
    // var searchParams = new URLSearchParams(window.location.search);
    // transferSearchParams[transferSearch] = newParams;
    frappe.call({
        method: "tourism_portal.api.search.get_transfer_search_results",
        args: {
            invoiceId: e.getAttribute("invoice-id"),
            transfer_params: newParams,
        },
        callback: res => {
            console.log(res)
            if (res.message){
                var  html = format_transfer_search_results(res.message)
                var modalContent = e.closest('.modal-content')
                modalContent.querySelector('.modal-body .transfer_search_card').classList.add('d-none');
                var resultsContainer = modalContent.querySelector('.modal-body .trasnfer_results')
                resultsContainer.innerHTML = html;
                resultsContainer.classList.remove('d-none');
                modalContent.querySelector('.search-transfer-btn').classList.add('d-none');
                modalContent.querySelector('.add-transfer-btn').classList.remove('d-none');
            }
            toggleLoadingIndicator(false);
            //window.location.reload();
        }
    })

}

function closeTransferModal(e){
    var modalContent = e.closest('.modal-content')
    modalContent.querySelector('.modal-body .transfer_search_card').classList.remove('d-none');
    modalContent.querySelector('.modal-body .trasnfer_results').classList.add('d-none');
    modalContent.querySelector('.search-transfer-btn').classList.remove('d-none');
    modalContent.querySelector('.add-transfer-btn').classList.add('d-none');
    $('#transferSearchModal').modal('hide');
}

function addNewTransferClicked(e){
    frappe.confirm("Are you sure you want to add these transfers to the invoice?", ()=> confirmAddTransfer(e))
}

function confirmAddTransfer(e){
    var selectedTransfers = getSelectedTransfers(e);
    // toggleLoadingIndicator(true);
    var invoiceId= new URLSearchParams(window.location.search).get('invoice');
    frappe.call({
        method: "tourism_portal.api.reserve.add_transfers_to_completed_invoice",
        args: {
            invoice_id: invoiceId,
            selected_transfers: selectedTransfers,
        },
        callback: res => {
            console.log(res)
            toggleLoadingIndicator(false);
            if (res.message && res.message.success_key){
                window.location.reload();
            }else if (res.message && !res.message.success_key){
                frappe.throw(res.message.message)
            }else{
                frappe.throw("Something went wrong")
            }
            
        }
    })
}

function transferTypeChanged(e) {
    if (e.value == 'group') {
        e.closest('form').querySelector('.allowed-flights').style.display = 'block';
    } else {
        e.closest('form').querySelector('.allowed-flights').style.display = 'none';
    }
}

function format_transfer_search_results(results){
    var html = '';
    for (var searchResult in results){
        var result = results[searchResult];
        html += format_transfer_search_one_result(result, searchResult);
    }

    return html;
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
    priceContainer.setAttribute('transfer-price-company', selectedOption.getAttribute('transfer_price_company'));
    transferCard.setAttribute('transfer-type', selectedOption.getAttribute('transfer_type_id'));
    transferCard.setAttribute('transfer-price', selectedOption.getAttribute('transfer_price'));
    transferCard.setAttribute('transfer-price-company', selectedOption.getAttribute('transfer_price_company'));
}

function format_transfer_search_one_result(results, searchResult){
    var html = '';
    var options = '';
    for (var resultNo in results){
        var result = results[resultNo];
        var selected = '';
        if (resultNo == 0){
            selected = 'selected';
        }
        options += `<option ${selected}
        transfer_type_id="${result.transfer_type}"
        transfer_type_name="${result.transfer_details.transfer_type}"
        transfer_price="${result.transfer_price}"
        transfer_price_company="${result.transfer_price_company}"
        from_postal_code="${result.search_params.from_postal_code}"
        to_postal_code="${result.search_params.to_postal_code}"
        flight_no="${result.search_params.params['flight-no'] || ''}"
        transfer_image="${result.transfer_details.transfer_image}"
        transfer_description="${result.transfer_details.transfer_description ||''}"
        from_location="${result.search_params.params['from-location']}"
        to_location="${result.search_params.params['to-location']}"
        transfer_date="${result.search_params.params['transfer-date']}"
    >${result.transfer_details.transfer_type} - ${result.transfer_price_company}</option>`;
    }
    var result = results[0];
    var resultTemplate = $('#transfer-card-template');
    var resultHtml = resultTemplate.html();
    resultHtml = resultHtml.replaceAll('{transferName}', searchResult);
    resultHtml = resultHtml.replaceAll('{transfer_transfer_type}', result.transfer_type);
    resultHtml = resultHtml.replaceAll('{transfer_transfer_price}', result.transfer_price);
    resultHtml = resultHtml.replaceAll('{transfer_transfer_price_company}', result.transfer_price_company);
    resultHtml = resultHtml.replaceAll('{search_params_from_postal_code}', result.search_params.from_postal_code);
    resultHtml = resultHtml.replaceAll('{search_params_to_postal_code}', result.search_params.to_postal_code);
    resultHtml = resultHtml.replaceAll('{params_flight-no}', result.search_params.params['flight-no'] || '');
    resultHtml = resultHtml.replaceAll('{transfer_details_transfer_image}', result.transfer_details.transfer_image);
    resultHtml = resultHtml.replaceAll('{transfer_details_transfer_type}', result.transfer_details.transfer_type);
    resultHtml = resultHtml.replaceAll('{transfer_details_transfer_description}', result.transfer_details.transfer_description || '');
    resultHtml = resultHtml.replaceAll('{params_from-location}', result.search_params.params['from-location']);
    resultHtml = resultHtml.replaceAll('{params_to-location}', result.search_params.params['to-location']);
    resultHtml = resultHtml.replaceAll('{params_from-location-name}', result.search_params.params['from-location-name']);
    resultHtml = resultHtml.replaceAll('{params_to-location-name}', result.search_params.params['to-location-name']);

    resultHtml = resultHtml.replaceAll('{paxes_adults}', result.search_params.params['paxes']['adults']);
    resultHtml = resultHtml.replaceAll('{paxes_children}', result.search_params.params['paxes']['children']);
    var total = Number(result.search_params.params['paxes']['adults']) + Number(result.search_params.params['paxes']['children']);
    resultHtml = resultHtml.replaceAll('{total_pax}', total);

    resultHtml = resultHtml.replaceAll('{params_transfer-date}', result.search_params.params['transfer-date']);
    resultHtml = resultHtml.replaceAll('{options}', options);
    // resultHtml = resultHtml.replaceAll('{to_location}', result.to_location);
    // resultHtml = resultHtml.replaceAll('{transfer_date}', result.transfer_date);
    // resultHtml = resultHtml.replaceAll('{transfer_time}', result.transfer_time);
    // resultHtml = resultHtml.replaceAll('{transfer_price}', result.transfer_price);

    html += resultHtml;
    return html;
}


function getSelectedTransfers(e){
    var transferResults = e.closest('.modal-content').querySelectorAll('.transfer-card')   
    var params = getTransferSearchInfo(e.closest('.modal-content').querySelector('.transfer-search-card'), true);
    var selectedTransfers = {}
    for (var transferResult of transferResults){
        var transferName = transferResult.getAttribute('transfer-name')
        selectedTransfers[transferName] = getCardSearchResults(transferResult, params[transferName])
    }
    return selectedTransfers
}

function getCardSearchResults(transferCard, transferParams){
    var searchResults = {}

    searchResults['transfer_type'] = transferParams['transfer-type'];
    searchResults['pick_up'] = transferParams['from-location'];
    searchResults['drop_off'] = transferParams['to-location'];
    searchResults['pick_up_type'] = transferParams['from-location-type'];
    searchResults['drop_off_type'] = transferParams['to-location-type'];
    searchResults['transfer_date'] = transferParams['transfer-date'];
    searchResults['pax_info'] = {};
    searchResults['pax_info']['adults'] = transferParams['paxes']['adults'];
    searchResults['pax_info']['children'] = transferParams['paxes']['children'];
    searchResults['pax_info']['childrenInfo'] = transferParams['paxes']['child-ages'];
    searchResults['transfer_id'] = transferCard.getAttribute('transfer-type');
    searchResults['transfer_price'] = transferCard.getAttribute('transfer-price');
    searchResults['transfer_price_company'] = transferCard.getAttribute('transfer-price-company');
    searchResults['pick_up_postal_code'] = transferCard.getAttribute('from-postal-code');
    searchResults['drop_off_postal_code'] = transferCard.getAttribute('to-postal-code');
    searchResults['flight_no'] = transferCard.getAttribute('flight-no');
    
    return searchResults
}

function validateReservationData(){
    var uncompleatedForm = false;
    $("select[name='pax-salut']").each(function(index, element) {
      if (element)
        uncompleatedForm = validateInput($(element)) ? uncompleatedForm: true;
    })
    $("input[name='pax-name']").each(function(index, element) {
      if (element)
        uncompleatedForm = validateInput($(element)) ? uncompleatedForm: true;
    })
    // uncompleatedForm = validateRadioInputSelected('room-bed-list') ? uncompleatedForm: true;
    // uncompleatedForm = validateRadioInputSelected('room-board-list') ? uncompleatedForm: true;
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
      var flightNode = transfer.querySelector('input[name="flight-no"]')
      if (flightNode && !flightNode.hasAttribute('disabled')){
        var flightNo = flightNode.value
        transfersInfo[transferSearch][transferName]['flight_no'] = flightNo
    }
      
      
      for (var pax of paxes){
        if (pax.querySelector('input[name="pax-name"]').hasAttribute('disabled')){
            continue;
        }
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
        if (pax.querySelector('input[name="pax-name"]').hasAttribute('disabled')){
            continue;
        }
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