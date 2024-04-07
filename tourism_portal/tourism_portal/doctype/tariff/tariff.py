# Copyright (c) 2024, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from tourism_portal.api.company import get_company_details
from tourism_portal.utils import publish_agency_notification

class Tariff(Document):
	def on_update(self):
		self.publish_notification()
	def publish_notification(self):	
		send_notification = frappe.db.get_single_value("Portal Notification Settings", "send_tariff_change_notification")		
		if not send_notification:
			return
		old_doc = self.get_doc_before_save()
		title = "Tariff Changed"
		notification = "Tariff with name {0} has been changed".format(self.name)
		if not old_doc:
			title = "New Tariff Published"
			notification = "Tariff with name {0} has been published".format(self.name)
		users = frappe.db.sql("""
				SELECT DISTINCT user.email
				FROM `tabUser` user
				INNER JOIN `tabCompany` company ON user.company = company.name
				INNER JOIN `tabCompany Assigned Class` company_class ON company.name = company_class.company
				WHERE 
						company_class.company_class = %(class_name)s AND company_class.city = %(city)s
						AND company.disabled = 0 AND user.enabled = 1
						AND company.country = %(country)s
		""", {"class_name": self.company_class, "city": self.city, "country": self.company_country}, as_dict=True, pluck=True)
		# users = frappe.db.get_values("User", {"company":["!=", ""], "enabled": 1}, "email", pluck=True)
		publish_agency_notification(
			title, 
			notification, "Tariff", self.name,users)


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
	country = frappe.db.get_value("Company", company, "country")
	for company_class in company_classes:
		_tariffs = get_tariff(company_class.get("company_class"), company_class.get("city"), country)
		for tariff in _tariffs:
			if tariff:
				tariffs.append({
					"company_class": company_class.get("company_class"),
					"city": company_class.get("city"),
					"tariff": tariff
				})
	return tariffs
def get_tariff(company_class, city, country):
	tariff = frappe.db.get_all("Tariff", {"company_class": company_class, "city": city,
										 "company_country": country,
									 "published_from_date": ["<=", frappe.utils.nowdate()],
									  "published_to_date": [">=", frappe.utils.nowdate()] }, 
									  ["name","tariff_from_date", "tariff_to_date",   "tariff_file"])
	return tariff