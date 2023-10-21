import frappe
from frappe import _
from tourism_portal.utils import get_portal_setting
import json
def get_context(context):
	if frappe.session.user == "Guest":
		frappe.throw(_("Log in to access this page."), frappe.PermissionError)
	params = frappe.form_dict.params
	params = json.loads(params)
	
	context.rooms = get_available_hotel_rooms(params)
	
	return context

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
def get_available_hotel_rooms(search_params):
	
	hotels = []
	for hotel in search_params:
		avilables = search_for_available_hotel(hotel)
		hotels.append(avilables)
	return hotels

"""
		
"""

def search_for_available_hotel(hotel_params):
	if not hotel_params.get('paxInfo'): return []
	condation = "AND tbl1.area=%(location)s"
	if hotel_params.get('location-type') == 'hotel':
		condation = 'AND tbl1.name=%(location)s'
	all_hotels = hotels = frappe.db.sql("""
		select 
		tbl1.name as hotel_id, tbl1.hotel_name, 
		tbl2.room_type, tbl2.room_accommodation_type, 
		tbl2.name as room_id,
		cntrct.name as contract_id,
		file.file_url as room_image,
		IFNULL(cntrct.accommodation_type_rule, tbl1.hotel_accommodation_type_rule) as hotel_accommodation_type_rule
		FROM `tabHotel Room` tbl2 
		INNER JOIN `tabHotel` tbl1 ON tbl1.name=tbl2.hotel
		LEFT JOIN `tabHotel Room Contract` cntrct ON cntrct.hotel=tbl2.hotel AND cntrct.room_type=tbl2.room_type AND 
			(cntrct.check_in_from_date is null or %(checkin)s BETWEEN cntrct.check_in_from_date and cntrct.check_in_to_date) AND
			( %(checkout)s BETWEEN cntrct.check_in_from_date and cntrct.check_in_to_date) AND
			(cntrct.selling_from_date  is null or now() BETWEEN cntrct.selling_from_date and cntrct.selling_to_date)
		LEFT JOIN `tabFile` as file on file.attached_to_name=tbl2.name AND file.attached_to_doctype='Hotel Room'
		WHERE	tbl2.disabled=0 AND tbl1.disabled=0 {condation}
		;
	""".format(condation=condation), {"location": hotel_params.get('location'), 
				   'checkin': hotel_params.get('checkin'), 'checkout': hotel_params.get('checkout')}, as_dict=True)
	hotels = {}
	for hotel in all_hotels:
		if not hotels.get(hotel.get('hotel_id')):
			hotels[hotel.get('hotel_id')] = []
		hotels[hotel.get('hotel_id')].append(hotel)
	availables = {}
	for name, hotel in hotels.items():
		if rooms := search_for_available_room(hotel_params.get('paxInfo'), hotel):
			availables[name] = rooms
	# for pax_info in hotel_params.get('paxInfo'):
	# 	availables = search_for_available_room(pax_info, all_hotels)
	# 	hotels.append(availables)

	return availables

def search_for_available_room(pax_info, hotel_rooms):
	suitable_rooms = {}
	all_found = True
	for pax in pax_info:
		all_found = False
		for room in hotel_rooms:
			if is_hotel_suitable(pax, room):
				all_found = True
				if not suitable_rooms.get(pax.get('roomName')):
					suitable_rooms[pax.get('roomName')] = []
				suitable_rooms[pax.get('roomName')].append(room)
		if not all_found: break
	return suitable_rooms if all_found else []
	
def is_hotel_suitable(pax_info, hotel):
	hotel_acmnd = frappe.db.sql("""
	SELECT
	tbl4.max_pax, tbl4.min_pax, tbl4.max_adults, tbl4.min_adults, tbl4.max_childs, tbl4.min_childs, tbl4.max_child_age
		FROM `tabRoom Accommodation Type Item` tbl4 
		 WHERE tbl4.parent=%(accommodation_rule)s and tbl4.room_type=%(room_accommodation_type)s 
	""", {"accommodation_rule": hotel.get('hotel_accommodation_type_rule'), 
       	"room_accommodation_type": hotel.get('room_accommodation_type')}, as_dict=True)

	if len(hotel_acmnd) < 1: return False

	adults =int(pax_info.get('adults'))
	children = int(pax_info.get('children'))
	for childPax in pax_info.get('childrenInfo'):
		if hotel_acmnd[0].get('max_child_age'):
			if int(childPax) > hotel_acmnd[0].get('max_child_age'):
				adults += 1
				children -= 1
	
	pax = adults + children
	if pax < hotel_acmnd[0].get('min_pax') or pax > hotel_acmnd[0].get('max_pax'): return False
	if adults < hotel_acmnd[0].get('min_adults') or adults > hotel_acmnd[0].get('max_adults'): return False
	if children < hotel_acmnd[0].get('min_childs') or children > hotel_acmnd[0].get('max_childs'): return False
	return True