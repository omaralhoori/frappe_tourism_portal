# Copyright (c) 2024, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from tourism_portal.api.company import get_company_details

class Turf(Document):
	pass


def get_company_turfs(company=None):
	if not company:
		company_details = get_company_details()
		if company_details.get('is_child_company'):
			return []
		company = company_details.get('company')
	company_classes = frappe.db.get_all(
		"Company Assigned Class", 
		{"company": company,
    "from_date": ["<=", frappe.utils.nowdate()],
	  "to_date": [">=", frappe.utils.nowdate()]}, 
	  ["company_class", "city"])
	turfs = []
	for company_class in company_classes:
		turf = get_turf(company_class.get("company_class"), company_class.get("city"))
		if turf:
			turfs.append({
				"company_class": company_class.get("company_class"),
				"city": company_class.get("city"),
				"turf": turf
			})
	return turfs
def get_turf(company_class, city):
	turf = frappe.db.get_value("Turf", {"company_class": company_class, "city": city, 
									 "published_from_date": ["<=", frappe.utils.nowdate()],
									  "published_to_date": [">=", frappe.utils.nowdate()] }, 
									  ["name","turf_from_date", "turf_to_date",   "turf_file"], as_dict=True)
	return turf