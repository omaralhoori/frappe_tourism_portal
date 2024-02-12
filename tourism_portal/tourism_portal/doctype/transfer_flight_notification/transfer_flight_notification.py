# Copyright (c) 2024, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TransferFlightNotification(Document):
	def after_insert(self):
		company = frappe.get_doc("Sales Invoice", self.sales_invoice).company
		company = frappe.get_doc("Company", company)
		if not company.reservation_email:
			return
		msg = "Please make sure to check the flight details for the transfer from " + self.pickup + " to " + self.dropoff + " on " + str(self.transfer_date)
		if self.flight_no:
			msg = "Flight No: " + self.flight_no + "\n" + msg 
		frappe.sendmail(
			recipients=[company.reservation_email],
			doctype="Sales Invoice",
			name=self.sales_invoice,
			message=msg,
			subject="Transfer Flight Notification For: " + self.sales_invoice,
			now=1,
		)
