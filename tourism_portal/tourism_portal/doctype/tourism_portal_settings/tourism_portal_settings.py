# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
import frappe.defaults

from frappe.model.document import Document


portal_keydict = {
	# "key in defaults": "key in Global Defaults"
	"hotel_cancellation_policy": "default_hotel_cancellation_policy",
	"hotel_accommodation_type_rule": "default_hotel_accommodation_type_rule",
	"hotel_child_rate_policy": "default_hotel_child_rate_policy",
	"hotel_profit_margin": "default_hotel_profit_margin",
	"currency": "selling_currency",
}


class TourismPortalSettings(Document):
	def on_update(self):
		"""update defaults"""
		for key in portal_keydict:
			frappe.db.set_default(key, self.get(portal_keydict[key], ""))

		# clear cache
		frappe.clear_cache()

	def get_defaults(self):
		return frappe.defaults.get_defaults()
