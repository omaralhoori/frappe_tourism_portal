import frappe
from frappe import _
import json

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    params = frappe.form_dict.params
    params = json.loads(params)
    rooms = json.loads(frappe.form_dict.rooms)
    print(rooms)