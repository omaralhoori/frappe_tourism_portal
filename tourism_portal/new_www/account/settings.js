
function onUpdatePasswordFormSubmit(e){
    var form = e.closest('form');
    console.log(form);
    var passwordData = getPasswordData(form);
    validatePasswordData(passwordData);
    frappe.call({
        method: 'tourism_portal.www.account.settings.updatePassword',
        args: {
            old_password: passwordData.oldPassword,
            new_password: passwordData.newPassword
        },
        callback: function(r){
            if (r.message && r.message.success_key) {
                showSuccessModal('Success', 'Your password has been updated successfully')
                form.querySelector('#inputPasswordOld').value = '';
                form.querySelector('#inputPasswordNew').value = '';
                form.querySelector('#inputPasswordNewVerify').value = '';
            }else if (r.message && !r.message.success_key) {
                frappe.throw(r.message.message);
            }else{
                frappe.throw('Something went wrong');
            }
        }
    })
    
}



function getPasswordData(form){
    var data = {};
    data.oldPassword = form.querySelector('#inputPasswordOld').value;
    data.newPassword = form.querySelector('#inputPasswordNew').value;
    data.newPasswordRepeat = form.querySelector('#inputPasswordNewVerify').value;
    return data;
}
//The password must be 8-20 characters, and must not contain spaces.
function validatePasswordData(data){
    if (!data.oldPassword) {
        frappe.throw('Please enter your old password');
        return false;
    }
    if (!data.newPassword) {
        frappe.throw('Please enter your new password');
        return false;
    }
    if (!data.newPasswordRepeat) {
        frappe.throw('Please repeat your new password');
        return false;
    }
    if (data.newPassword !== data.newPasswordRepeat) {
        frappe.throw('New passwords do not match');
        return false;
    }
    if (data.newPassword.length < 8) {
        frappe.throw('Password must be at least 8 characters long');
        return false;
    }
    if (data.newPassword.length > 20) {
        frappe.throw('Password cannot be longer than 20 characters');
        return false;
    }
    if (data.newPassword.indexOf(' ') >= 0) {
        frappe.throw('Password cannot contain spaces');
        return false;
    }
    return true;
}