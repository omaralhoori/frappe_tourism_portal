import frappe


def get_portal_setting(fieldname):
    return frappe.db.get_single_value("Tourism Portal Settings", fieldname)

def get_site_logo():
    return frappe.db.get_single_value("Website Settings", "brand_html")

def get_site_name():
    return frappe.db.get_single_value("")

def get_room_extras(hotel):
    return frappe.db.get_all("Hotel Extra Service Item", {"parent": hotel}, ['service', 'extra_price_type', 'extra_price'])

def delete_expired_invoices():
    expired_invoices = frappe.db.get_all("Sales Invoice", {"session_expires": ["<", frappe.utils.now()], "docstatus": 0})
    for invoice in expired_invoices:
        frappe.delete_doc("Sales Invoice", invoice['name'], ignore_permissions=True)
        # frappe.db.commit()