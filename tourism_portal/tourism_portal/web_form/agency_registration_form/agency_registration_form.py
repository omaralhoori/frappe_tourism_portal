import frappe

def get_context(context):
	context.no_cache = True
	context.terms_and_conditions = frappe.db.get_single_value("Tourism Portal Settings", "agency_terms_and_conditions")
