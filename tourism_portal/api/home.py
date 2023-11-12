import frappe


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