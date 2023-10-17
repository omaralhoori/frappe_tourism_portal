# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from tourism_portal.utils import get_portal_setting

def get_context(context):
	if frappe.session.user == "Guest":
		frappe.throw(_("Log in to access this page."), frappe.PermissionError)
	
	context.locations = get_locations()
	context.nationalities = frappe.db.get_all("Nationality")
	context.max_rooms = get_portal_setting("max_hotel_rooms_selected")
	context.max_room_adults = get_portal_setting("max_adults_per_room")
	context.max_room_children = get_portal_setting("max_children_per_room")
	return context


def get_locations():
	locations = {
		"hotels": {},
	}

	hotels = frappe.db.sql("""
		SELECT tbl1.name as location_id, tbl1.hotel_name as location_name, tbl1.area as area_id, tbl2.area_name
		FROM `tabHotel` as tbl1
		INNER JOIN `tabArea` as tbl2 ON tbl1.area=tbl2.name
		WHERE tbl1.disabled=0
	""", as_dict=True)
	# areas = [{"location_id": hotel.get('area_id'), "location_name": hotel.get('area_name')} for hotel in hotels]
	for hotel in hotels:
		if not locations['hotels'].get(hotel.get('area_id')):
			locations['hotels'][hotel.get('area_id')] = []
		locations['hotels'][hotel.get('area_id')].append(hotel)
	# locations['hotels']['hotels'] = hotels
	# locations['hotels']['areas'] = areas
	print(locations)
	return locations
