import frappe


def get_portal_setting(fieldname):
    return frappe.db.get_single_value("Tourism Portal Settings", fieldname)

def get_site_logo():
    return frappe.db.get_single_value("Website Settings", "brand_html")

def get_site_name():
    return frappe.db.get_single_value("")