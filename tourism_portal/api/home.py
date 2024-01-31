import frappe
from frappe.desk.form.load import get_attachments
from tourism_portal.utils import get_location_city, get_location_postal_code, get_postal_code_transfer_area
import json

@frappe.whitelist(allow_guest=True)
def get_locations(search="", start=0, page_len=20):
	locations = {
		"hotels": {},
	}

	hotels = frappe.db.sql("""
		SELECT tbl1.name as location_id, tbl1.hotel_name as location_name, tbl1.area as area_id, tbl2.area_name
		FROM `tabHotel` as tbl1
		INNER JOIN `tabArea` as tbl2 ON tbl1.area=tbl2.name
		WHERE tbl1.disabled=0 AND (tbl1.hotel_name like %(txt)s or tbl2.area_name like %(txt)s)
        limit {page_len} offset {start}
	""".format(page_len=page_len, start=start),{"txt": "%%%s%%" % search}, as_dict=True)
	areas = [{"location_id": hotel.get('area_id'), "location_name": hotel.get('area_name')} for hotel in hotels]
	locations['hotels']['hotels'] = hotels
	locations['hotels']['areas'] = areas
	return locations


@frappe.whitelist(allow_guest=True)
def get_nationalities(search="", start=0, page_len=20):
    return frappe.db.sql("""
		SELECT name
		FROM `tabNationality` as tbl1
		WHERE name like %(txt)s
        limit {page_len} offset {start}
	""".format(page_len=page_len, start=start),{"txt": "%%%s%%" % search}, as_dict=True)

@frappe.whitelist(allow_guest=True)
def get_home_settings():
	max_room = frappe.db.get_single_value("Tourism Portal Settings", "max_hotel_rooms_selected")
	max_adults = frappe.db.get_single_value("Tourism Portal Settings", "max_adults_per_room")
	max_children = frappe.db.get_single_value("Tourism Portal Settings", "max_children_per_room")

	return {
			"hotel_settings": {
				"max_room": max_room,
				"max_adults": max_adults,
				"max_children": max_children
			}
	}

@frappe.whitelist()
def get_available_tours():
	params = frappe.form_dict.tourData
	if type(params) == str:
		params = json.loads(params)
	where_stmt = ""
	if params.get('tour-type') == 'vip':
		where_stmt = "AND tbl1.tour_type='VIP'"
	elif params.get('tour-type') == 'group-premium':
		where_stmt = "AND tbl1.tour_type='Premium'"
	elif params.get('tour-type') == 'group-economic':
		where_stmt = "AND tbl1.tour_type='Economic'"
	city = get_location_city(params['location-type'], params['location'])
	postal_code = get_location_postal_code(params['location-type'], params['location'])
	total_days = frappe.utils.date_diff( params['checkout'], params['checkin'],) + 1
	if params.get('tour-type') in ['group-premium', 'group-economic', 'package']:
		if not frappe.db.get_value("Postal Code", postal_code, 'regular_transport'):
			return {}
	# tours = frappe.db.sql("""
	# 		   SELECT tbl1.name as tour_id, tbl1.tour_name as tour_name, 
	# 		   tbl1.tour_description as tour_description, tbl2.schedule_date as tour_date
	# 		   FROM `tabTour Schedule` as tbl2
	# 		   INNER JOIN `tabTour Type` as tbl1 ON tbl2.tour_type=tbl1.name
	# 		   WHERE tbl1.disabled=0 AND tbl2.city=%(city)s AND tbl2.schedule_date between %(from_date)s AND %(to_date)s {where_stmt}
	# 		   """.format(where_stmt=where_stmt), {"city": city, "from_date": params['checkin'], "to_date": params['checkout']}, as_dict=True)
	pacages, tours = [], []
	if params.get('tour-type') == 'package':
		pacages = frappe.db.sql("""
	SELECT tbl1.name as tour_id, tbl1.package_name as tour_name, tbl1.description as tour_description, tbl1.min_days as tour_time
						  FROM `tabTour Package` as tbl1
	WHERE tbl1.disabled=0 AND tbl1.package_city=%(city)s AND tbl1.min_days<={total_days} AND tbl1.from_date <= %(tour_date)s AND tbl1.to_date >= %(tour_date)s
	""".format(total_days=total_days), {"city": city, "tour_date": params.get('checkin')}, as_dict=True)
	else:
		tours = frappe.db.sql("""
			   SELECT tbl1.name as tour_id, tbl1.tour_name as tour_name, tbl1.tour_description as tour_description, tbl1.tour_time as tour_time
			   FROM `tabTour Type` as tbl1
			   WHERE tbl1.disabled=0 AND tbl1.tour_pickup_city=%(city)s {where_stmt}
			   """.format(where_stmt=where_stmt), {"city": city, "from_date": params['checkin'], "to_date": params['checkout']}, as_dict=True)
	available_tours = {}
	for tour in tours:
		if not available_tours.get(tour.get('tour_id')):
			available_tours[tour.get('tour_id')] = {}
			available_tours[tour.get('tour_id')]['tour_id'] = tour.get('tour_id')
			available_tours[tour.get('tour_id')]['tour_name'] = tour.get('tour_name')
			available_tours[tour.get('tour_id')]['tour_description'] = tour.get('tour_description')
			available_tours[tour.get('tour_id')]['tour_time'] = tour.get('tour_time')
			available_tours[tour.get('tour_id')]['tour_dates'] = []
	for tour in pacages:
		if not available_tours.get(tour.get('tour_id')):
			available_tours[tour.get('tour_id')] = {}
			available_tours[tour.get('tour_id')]['tour_id'] = tour.get('tour_id')
			available_tours[tour.get('tour_id')]['tour_name'] = tour.get('tour_name')
			available_tours[tour.get('tour_id')]['tour_description'] = tour.get('tour_description')
			available_tours[tour.get('tour_id')]['tour_time'] = tour.get('tour_time')
			available_tours[tour.get('tour_id')]['tour_dates'] = []
	return available_tours

@frappe.whitelist()
def get_regular_flights(location, route):
	flights = frappe.db.get_all("Flight", {route: location, "is_regular": 1}, ['name'])
	return flights

@frappe.whitelist()
def create_search(hotelParams, transferParams, tourParams):
	print(transferParams)
	search_doc = frappe.get_doc({
		"doctype": "Search Result",
		"hotel_params": hotelParams,
		"transfer_params": transferParams,
		"tour_params": tourParams,
		"user": frappe.session.user
	})
	search_doc.insert(ignore_permissions=True)
	return {
		"is_success": True,
		"search_name": search_doc.name
	}


@frappe.whitelist()
def get_tour_info(tour_id, tour_type):
	doctype = "Tour Type"
	fields = ["tour_name", "tour_description", "tour_image"]
	if tour_type == 'package':
		doctype = "Tour Package"
		fields = ["package_name as tour_name", "description as tour_description", "package_image as tour_image"]
	tour_info = frappe.db.get_value(doctype, tour_id, fields, as_dict=True)
	attachments = get_attachments(doctype, tour_id)
	
	return {
		"tour_info": tour_info,
		"attachments": attachments
	}
@frappe.whitelist()
def get_packge_tour_info(tours, tour_type):
	return {}
	# doctype = "Tour Type"
	# fields = ["tour_name", "tour_description", "tour_image"]
	# if tour_type == 'package':
	# 	doctype = "Tour Package"
	# 	fields = ["package_name as tour_name", "description as tour_description", "package_image as tour_image"]
	# result = []
	# tour_info = frappe.db.get_value(doctype, tour_id, fields, as_dict=True)
	
	# #attachments = get_attachments(doctype, tour_id)
	
	# return {
	# 	"tour_info": tour_info,
	# #	"attachments": attachments
	# }