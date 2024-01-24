# Copyright (c) 2024, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from tourism_portal.api.company import get_company_details

class Tariff(Document):
	pass


def get_company_tariffs(company=None):
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
	tariffs = []
	for company_class in company_classes:
		tariff = get_tariff(company_class.get("company_class"), company_class.get("city"))
		if tariff:
			tariffs.append({
				"company_class": company_class.get("company_class"),
				"city": company_class.get("city"),
				"tariff": tariff
			})
	return tariffs
def get_tariff(company_class, city):
	tariff = frappe.db.get_value("Tariff", {"company_class": company_class, "city": city, 
									 "published_from_date": ["<=", frappe.utils.nowdate()],
									  "published_to_date": [">=", frappe.utils.nowdate()] }, 
									  ["name","tariff_from_date", "tariff_to_date",   "tariff_file"], as_dict=True)
	return tariff