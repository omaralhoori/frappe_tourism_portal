# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from tourism_portal.utils import publish_agency_notification

class HotelRoomPrice(Document):
	def on_update(self):
		self.publish_notification()
	def publish_notification(self):	
		send_notification = frappe.db.get_single_value("Tourism Portal Settings", "send_price_change_notification")		
		if not send_notification:
			return
		old_doc = self.get_doc_before_save()
		if not old_doc:
			return
		if old_doc.buying_price == self.buying_price and old_doc.selling_price == self.selling_price:
			return
		hotel_name = frappe.db.get_value("Hotel", self.hotel, "hotel_name", cache=True)
		room_type = frappe.db.get_value("Hotel Room Contract", self.room_contract, "room_type", cache=True)
		room_type_name = frappe.db.get_value("Room Type", room_type, "room_type", cache=True)
		room_acmnd = frappe.db.get_value("Room Accommodation Type", self.room_accommodation_type, "accommodation_type_name", cache=True)

		publish_agency_notification(
			"Price Changed for " + hotel_name, 
			f"Price for {room_type_name} {room_acmnd} in {hotel_name} has been changed betweem {self.check_in_from_date} and {self.check_in_to_date}", "Hotel Room Price", self.name, )