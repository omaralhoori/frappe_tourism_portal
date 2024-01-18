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

}

function cancelEdit(e){
    var invoiceId = e.getAttribute("invoice-id");
    window.location.href = "/reserve?invoice=" + invoiceId;
}
function addTransfer(e){
    var invoiceId = e.getAttribute("invoice-id");
    var $modal = $('#transferSearchModal');
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
            toggleLoadingIndicator(false);
            //window.location.reload();
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
