import frappe


@frappe.whitelist(allow_guest=True)
def get_locations(search="", start=0, page_len=10):
    hotels = frappe.db.sql("""
        SELECT town.name as locationId, town.town_name as locationName, 'town' AS locationType, 'Town' as locationDetails
        FROM `tabTown` as town
        WHERE town.town_name LIKE %(txt)s
        UNION
        SELECT area.name as locationId, area.area_name as locationName, 'area' AS locationType, 'Area' AS locationDetails
        FROM `tabArea` as area
        INNER JOIN `tabTown` as town ON area.town=town.name
        WHERE area.area_name LIKE %(txt)s or town.town_name LIKE %(txt)s
        UNION
        SELECT hotel.name as locationId, hotel.hotel_name as locationName, 'hotel' AS locationType, IFNULL(hotel.address, '') as locationDetails
        FROM `tabHotel` as hotel
        INNER JOIN `tabArea` as area ON hotel.area=area.name
        INNER JOIN `tabTown` as town ON area.town=town.name
        WHERE hotel.hotel_name LIKE %(txt)s or area.area_name LIKE %(txt)s or town.town_name LIKE %(txt)s
        LIMIT {page_len} OFFSET {start}
    """.format(page_len=page_len, start=start),{"txt": "%%%s%%" % search}, as_dict=True)
    return hotels

@frappe.whitelist(allow_guest=True)
def get_tour_locations(search="", start=0, page_len=10):
	hotels = frappe.db.sql("""
        SELECT area.name as locationId, area.area_name as locationName, 'area' AS locationType, 'Area' AS locationDetails
        FROM `tabArea` as area
		INNER JOIN `tabTown` as town ON area.town=town.name
        WHERE area.area_name LIKE %(txt)s or town.town_name LIKE %(txt)s
        UNION
        SELECT hotel.name as locationId, hotel.hotel_name as locationName, 'hotel' AS locationType, IFNULL(hotel.address, '') as locationDetails
        FROM `tabHotel` as hotel
        INNER JOIN `tabArea` as area ON hotel.area=area.name
        INNER JOIN `tabTown` as town ON area.town=town.name
        WHERE hotel.hotel_name LIKE %(txt)s or area.area_name LIKE %(txt)s or town.town_name LIKE %(txt)s
		LIMIT {page_len} OFFSET {start}
	""".format(page_len=page_len, start=start),{"txt": "%%%s%%" % search}, as_dict=True)
	return hotels


@frappe.whitelist(allow_guest=True)
def get_transfer_locations(search="", start=0, page_len=10):
	hotels = frappe.db.sql("""
		SELECT air.name as locationId, air.airport_name as locationName, 'airport' AS locationType, 'Airport' as locationDetails
        FROM `tabAirport` as air
        WHERE air.airport_name LIKE %(txt)s AND air.portal_disabled=0
        UNION
        SELECT area.name as locationId, area.area_name as locationName, 'area' AS locationType, 'Area' AS locationDetails
        FROM `tabArea` as area
		INNER JOIN `tabTown` as town ON area.town=town.name
        WHERE area.area_name LIKE %(txt)s or town.town_name LIKE %(txt)s
        UNION
        SELECT hotel.name as locationId, hotel.hotel_name as locationName, 'hotel' AS locationType, IFNULL(hotel.address, '') as locationDetails
        FROM `tabHotel` as hotel
        INNER JOIN `tabArea` as area ON hotel.area=area.name
        INNER JOIN `tabTown` as town ON area.town=town.name
        WHERE hotel.hotel_name LIKE %(txt)s or area.area_name LIKE %(txt)s or town.town_name LIKE %(txt)s
		LIMIT {page_len} OFFSET {start}
	""".format(page_len=page_len, start=start),{"txt": "%%%s%%" % search}, as_dict=True)
	return hotels