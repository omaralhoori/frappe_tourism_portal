function userModalSubmitted(e){
    var userData = getUserData(e)
    var errors = validateUserData(userData);
    if (errors.length > 0){
        frappe.throw(errors.join("\n"));
        return;
    }
    frappe.call({
        "method": "tourism_portal.api.user.create_update_user",
        "args": {
            "user_data": userData
        },
        "callback": function(response){
            if (response.message){
                frappe.msgprint(response.message);
                window.location.reload();
            }
        }
    })
}

function getUserData(e){
    var userData = {
        'fullname': $('#user-full-name').val(),
        'email': $('#user-email').val(),
        'password': $('#user-password').val(),
        'user_id': $('#user-id').val(),
        'action_type': $('#submit-modal').attr("action"),
    };
    return userData;
}   


function validateUserData(userData){
    var errors = [];
    if (userData.action_type == "create"){
    if (userData.fullname == ""){
        errors.push("Full name cannot be empty");
    }
    if (userData.email == ""){
        errors.push("Email cannot be empty");
    }
    if (userData.password == ""){
        errors.push("Password cannot be empty");
    }}
    else if (userData.action_type == "update"){
        if (userData.fullname == ""){
            errors.push("Full name cannot be empty");
        }
        if (userData.email == ""){
            errors.push("Email cannot be empty");
        }
    }
    return errors;
}