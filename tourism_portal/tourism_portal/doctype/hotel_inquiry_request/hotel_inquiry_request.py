# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from tourism_portal.utils import parse_date

class HotelInquiryRequest(Document):
	def before_insert(self):
		self.qty = self.requested_qty
		if len(self.hotel_inquiry_buying_price) == 0:
			hotel_inquiry_row = self.append("hotel_inquiry_buying_price")
			hotel_inquiry_row.from_date = self.from_date
			hotel_inquiry_row.to_date = frappe.utils.add_days(self.to_date, -1)
	def before_submit(self):
		self.validate_required_fields()
		self.valid_datetime = frappe.utils.now_datetime()+frappe.utils.datetime.timedelta(seconds=self.valid_until)
	def validate_required_fields(self):
		if not self.status:
			frappe.throw("Please enter Status field")
		if self.status == 'Available':
			if not self.valid_until:
				frappe.throw("Please enter Valid Until field")
			if len(self.hotel_inquiry_buying_price) == 0:
				frappe.throw("Please enter Buying details")
			self.validate_buying_price_dates()
		for price in self.hotel_inquiry_buying_price:
			if not price.buying_currency:
				frappe.throw("Please enter Buying Currency")
			if not price.buying_price:
				frappe.throw("Please enter Buying Price")
			if not price.from_date:
				frappe.throw("Please enter From Date")
			if not price.to_date:
				frappe.throw("Please enter To Date")
	def validate_buying_price_dates(self):
		start_date = self.from_date
		end_date = frappe.utils.add_days(self.to_date, -1)
		for price in self.hotel_inquiry_buying_price:
			if price.from_date > price.to_date:
				frappe.throw("From Date should be less than To Date")
			
	def update_buying_price(self, contracts, prices):
		for price in prices:
			room_contract = frappe.db.get_value("Hotel Room Price", price.get("priceId"), "room_contract", cache=True)
			contract_type = frappe.db.get_value("Hotel Room Contract", room_contract, "contract_type", cache=True)
			if  contract_type == "No Contract":
				price_row = self.append("hotel_inquiry_buying_price")
				price_doc = frappe.get_cached_doc("Hotel Room Price", price.get("priceId"))
				price_row.buying_currency = price_doc.buying_currency
				price_row.buying_price = price_doc.buying_price
				price_row.from_date = parse_date(price.get('fromDate'))
				price_row.to_date = parse_date(price.get('toDate'))
		