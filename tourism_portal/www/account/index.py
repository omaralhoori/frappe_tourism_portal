import frappe
from frappe import _

no_cache=1
def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    context.include_sidebar = True
    context.users = [
        {"username": "admin",
         "id":"1", 
         "name": "Administrator",
        "roles": [{"name": "System Manager"}, {"name": "Administrator"}]
         },
         {
            "username": "test",
            "id":"2",
            "name": "Test User",
            "roles": [{"name": "Blogger"}]
         },
         
    ]
    return context