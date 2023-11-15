import frappe
from frappe import auth
from frappe.core.doctype.user.user import update_password

@frappe.whitelist( allow_guest=True )
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Authentication Error!"
        }

        return
    user = frappe.get_doc('User', frappe.session.user)
    #if not user.api_secret:
    api_key, api_secert = generate_keys(frappe.session.user)
    # else:
    #     api_generate = user.api_secret
    
    frappe.response["message"] = {
        "success_key":1,
        "message":"Authentication success",
        "sid":frappe.session.sid,
        "api_key":api_key,
        "api_secret":api_secert,
        "username":user.username,
        "fullname": user.full_name,
        "image": user.user_image,
        "gender": user.gender,
        "address": user.location,
        "birth_date": user.birth_date,
        "mobile_no": user.mobile_no,
        "email":user.email,
    }


@frappe.whitelist()
def change_password(old_password, new_password):
    try:
        update_password(new_password=new_password, old_password=old_password)
        return "Password updated successfully"
    except:
        return "Failed to update password"

def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    if not user_details.secret_key:
        user_details.secret_key = api_secret
    user_details.api_secret = user_details.secret_key
    user_details.save(ignore_permissions=True)
    frappe.db.commit()
    return user_details.api_key, user_details.secret_key

@frappe.whitelist()
def get_user_name():
    return frappe.session.user