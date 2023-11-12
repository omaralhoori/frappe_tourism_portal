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