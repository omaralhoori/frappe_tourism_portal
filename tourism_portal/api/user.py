import frappe
from frappe.utils.password import update_password
import json

@frappe.whitelist()
def create_update_user():
    user_data = frappe.form_dict.user_data
    if type(user_data) == str:
        user_data = json.loads(user_data)
    if user_data.get('action_type') == 'create':
        create_user(user_data)
    elif user_data.get('action_type') == 'update':
        pass
        #update_user(user_data)
    return "successs"

def create_user(user_data):
    company = frappe.db.get_value("User", frappe.session.user, "company")
    user = frappe.new_doc("User")
    user.email = user_data.get('email')
    user.first_name = user_data.get('fullname')
    user.company = company
    user.append_roles(('Customer'))
    user.save()
    update_password(user=user.name, pwd=user_data.get('password'))