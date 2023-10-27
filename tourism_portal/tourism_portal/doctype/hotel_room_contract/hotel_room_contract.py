# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
class HotelRoomContract(Document):
	def on_submit(self):
		if self.check_in_from_date > self.check_in_to_date:
			frappe.throw("Check in to date is greater than check in from date")
		date_list = []
		if self.qty > 0:
			current_date = datetime.strptime(self.check_in_from_date, "%Y-%m-%d")
			to_date = datetime.strptime(self.check_in_to_date, "%Y-%m-%d")
			while current_date <= to_date:
				date_list.append(current_date)
				current_date += timedelta(days=1)
		self.create_room_availabilities(date_list)

	def create_room_availabilities(self, date_list):
		for date in date_list:
			frappe.get_doc({
				"doctype":"Room Availability",
				"contract_no": self.name,
				"date": date,
				"available_qty": self.qty
			}).insert(ignore_permissions=True)

	def on_cancel(self):
		frappe.db.delete("Room Availability", {"contract_no": self.name})
		frappe.db.delete("Hotel Room Price", {"room_contract": self.name})
			
