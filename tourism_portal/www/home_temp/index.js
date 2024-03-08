function submit_contact_form(e){
    var contact_name = $('#contact_form_name').val()
    var contact_email = $('#contact_form_email').val()
    var contact_subject = $('#contact_form_subject').val()
    var contact_message = $('#contact_form_message').val()
    if (!contact_name || !contact_email || !contact_subject || !contact_message){
        throwError("All fields are required")
    }
    toggleLoader(true)
    frappe.call({
        "method": "tourism_portal.www.home.index.submit_contact_form",
        "args": {
            "contact_name": contact_name,
            "contact_email": contact_email,
            "contact_subject": contact_subject,
            "contact_message": contact_message
        },
        callback: function(res){
            toggleLoader(false)
            if (res.message){
                $('#contact_form_name').val('')
                 $('#contact_form_email').val('')
                $('#contact_form_subject').val('')
                $('#contact_form_message').val('')
            }else{
               throwError("Something went wrong, please try again later")
            }
        }
    })
}