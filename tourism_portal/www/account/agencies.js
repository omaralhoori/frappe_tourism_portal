function agencyModalSubmitted(e){
    var agencyData = getAgencyData(e)
    var errors = getAgencyData(agencyData);
    if (errors.length > 0){
        frappe.throw(errors.join("\n"));
        return;
    }
    frappe.call({
        "method": "tourism_portal.api.company.create_agency",
        "args": {
            "agency_data": agencyData
        },
        "callback": function(response){
            if (response.message){
                frappe.msgprint(response.message);
                window.location.reload();
            }
        }
    })
}

function getAgencyData(e){
    var agencyData = {
        'agency_code': $('#agency-code').val(),
        'agency_name': $('#agency-name').val(),
        'fullname': $('#user-full-name').val(),
        'email': $('#user-email').val(),
        'password': $('#user-password').val(),
        'user_id': $('#user-id').val(),
        'action_type': $('#submit-modal').attr("action"),
    };
    return agencyData;
}   


function validateAgencyData(agencyData){
    var errors = [];
    if (agencyData.action_type == "create"){
    if (agencyData.agency_code == ""){
        errors.push("Agency Code cannot be empty");
    }
    if (agencyData.agency_name == ""){
        errors.push("Agency name cannot be empty");
    }
    if (agencyData.fullname == ""){
        errors.push("Full name cannot be empty");
    }
    if (agencyData.email == ""){
        errors.push("Email cannot be empty");
    }
    if (agencyData.password == ""){
        errors.push("Password cannot be empty");
    }}
    else if (agencyData.action_type == "update"){
        if (agencyData.fullname == ""){
            errors.push("Full name cannot be empty");
        }
        if (agencyData.email == ""){
            errors.push("Email cannot be empty");
        }
    }
    return errors;
}

function moneyModalSubmitted(e){
    var amount = $('#agency-amount').val();
    if (amount == "" || amount <= 0){
        frappe.throw("Amount cannot be empty or less than 0");
        return;
    }
    var agency = $('#agency-money-id').val();
    if (agency == ""){
        frappe.throw("Agency cannot be empty");
        return;
    }
    frappe.call({
        "method": "tourism_portal.api.company.add_agency_money",
        "args": {
            "amount": amount,
            "agency": agency
        },
        "callback": function(response){
            if (response.message){
                frappe.msgprint(response.message);
                window.location.reload();
            }
        }
    })
}

function addMoneyModalOpen(e){
    var agencyId = e.getAttribute("agency-id");
    $('#agency-money-id').val(agencyId);
    $('#money-modal').modal('show');
}

function profitModalOpen(e){
    var agencyId = e.getAttribute("agency-id");
    var hotelProfit = e.getAttribute("hotel-profit");
    var transferProfit = e.getAttribute("transfer-profit");
    var tourProfit = e.getAttribute("tour-profit");
    $('#agency-profit-id').val(agencyId);
    $('#agency-hotel-profit').val(hotelProfit);
    $('#agency-transfer-profit').val(transferProfit);
    $('#agency-tour-profit').val(tourProfit);
    $('#profit-modal').modal('show');
}

function profitModalSubmitted(e){
    var hotelProfit = $('#agency-hotel-profit').val();
    var transferProfit = $('#agency-transfer-profit').val();
    var tourProfit = $('#agency-tour-profit').val();
    var agency = $('#agency-profit-id').val();
    if (agency == ""){
        frappe.throw("Agency cannot be empty");
        return;
    }
    frappe.call({
        "method": "tourism_portal.api.company.update_agency_profit",
        "args": {
            "hotel_profit": hotelProfit,
            "transfer_profit": transferProfit,
            "tour_profit": tourProfit,
            "agency": agency
        },
        "callback": function(response){
            if (response.message){
                frappe.msgprint(response.message);
                window.location.reload();
            }
        }
    })
}