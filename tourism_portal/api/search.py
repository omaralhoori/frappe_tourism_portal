import frappe
from frappe import _
from tourism_portal.www.search.index import get_available_hotel_rooms
import json
"""
	search_params: [
		{
			location: ,
			location-type: ,
			nationality: ,
			checkin: ,
			checkout: ,
			room: ,
			paxInfo: [{
				adults: ,
				children: ,
				childrenInfo: [],
			}]
		}
	]
"""


@frappe.whitelist(allow_guest=True)
def get_available_hotels():
    search_params = frappe.form_dict.hotels_params#json.loads(frappe.form_dict)
    return get_available_hotel_rooms(search_params)


@frappe.whitelist()
def ask_for_availability(room_id, room_qty):
	now_datetime = frappe.utils.now()
	inquiries = frappe.db.sql("""
		select name from `tabHotel Inquiry Request`
		WHERE customer=%(customer)s AND room=%(room)s AND 
		(docstatus=0 OR valid_datetime > %(now_datetime)s)
	""", {"customer": frappe.session.user, "room": room_id, "now_datetime": now_datetime})
	if len(inquiries) > 0:
		return {
			"success_key": 0,
			"message": _("You have asked for this room before.")
		}
	frappe.get_doc({
		"doctype": "Hotel Inquiry Request", 
		"customer": frappe.session.user,
		"room": room_id,
		"qty": room_qty
	}).insert(ignore_permissions=True)
	return {
		"success_key": 1,
		"message": _("The request has been submitted successfully")
	}