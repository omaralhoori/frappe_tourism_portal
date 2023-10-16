import frappe


def get_portal_setting(fieldname):
    return frappe.db.get_single_value("Tourism Portal Settings", fieldname)