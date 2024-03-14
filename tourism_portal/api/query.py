import frappe


@frappe.whitelist(allow_guest=True)
def get_locations(search="", start=0, page_len=20):
    hotels = frappe.db.sql("""
        (SELECT city.name as locationId, city.city_name as locationName, 'city' AS locationType, '' as locationDetails
        FROM `tabCity` as city
        WHERE city.city_name LIKE %(txt)s and city.portal_disabled=0
						   ORDER BY 
			if(locate(%(_txt)s, city.name), locate(%(_txt)s, city.name), 99999),
			if(locate(%(_txt)s, city.city_name), locate(%(_txt)s, city.city_name), 99999)
        LIMIT {page_len} OFFSET {start}
						   )
		UNION
        (SELECT hotel.name as locationId, hotel.hotel_name as locationName, 'hotel' AS locationType, IFNULL(hotel.address, '') as locationDetails
						   FROM `tabHotel` as hotel
        INNER JOIN `tabArea` as area ON hotel.area=area.name
        INNER JOIN `tabTown` as town ON area.town=town.name
        WHERE hotel.hotel_name LIKE %(txt)s or area.area_name LIKE %(txt)s or town.town_name LIKE %(txt)s and hotel.disabled=0
		ORDER BY 
			if(locate(%(_txt)s, hotel.name), locate(%(_txt)s, hotel.name), 99999),
			if(locate(%(_txt)s, hotel.hotel_name), locate(%(_txt)s, hotel.hotel_name), 99999)
		LIMIT {page_len} OFFSET {start})				   
            UNION
        (SELECT town.name as locationId, town.town_name as locationName, 'town' AS locationType, CONCAT(town.city, ', Town') as locationDetails
        FROM `tabTown` as town
        WHERE town.town_name LIKE %(txt)s and town.portal_disabled=0
						   ORDER BY 
			if(locate(%(_txt)s, town.name), locate(%(_txt)s, town.name), 99999),
			if(locate(%(_txt)s, town.town_name), locate(%(_txt)s, town.town_name), 99999)
        LIMIT {page_len} OFFSET {start}
						   )
						   UNION
						   (
        SELECT area.name as locationId, area.area_name as locationName, 'area' AS locationType, CONCAT(area.city, ", ", area.town) AS locationDetails
        FROM `tabArea` as area
        INNER JOIN `tabTown` as town ON area.town=town.name
        WHERE area.area_name LIKE %(txt)s or town.town_name LIKE %(txt)s and area.portal_disabled=0
						   ORDER BY 
			if(locate(%(_txt)s, area.name), locate(%(_txt)s, area.name), 99999),
			if(locate(%(_txt)s, area.area_name), locate(%(_txt)s, area.area_name), 99999)
LIMIT {page_len} OFFSET {start}						   )
    """.format(page_len=page_len, start=start),{"txt": "%%%s%%" % search, '_txt': search}, as_dict=True)
    return hotels

@frappe.whitelist(allow_guest=True)
def get_tour_locations(search="", start=0, page_len=10):
	hotels = frappe.db.sql("""
		(
        SELECT area.name as locationId, area.area_name as locationName, 'area' AS locationType, CONCAT(area.city, ", ", area.town) AS locationDetails
        FROM `tabArea` as area
		INNER JOIN `tabTown` as town ON area.town=town.name
        WHERE area.area_name LIKE %(txt)s or town.town_name LIKE %(txt)s and area.portal_disabled=0
        ORDER BY 
			if(locate(%(_txt)s, area.name), locate(%(_txt)s, area.name), 99999),
			if(locate(%(_txt)s, area.area_name), locate(%(_txt)s, area.area_name), 99999)
		LIMIT {page_len} OFFSET {start}
		)
        UNION
		(
        SELECT hotel.name as locationId, hotel.hotel_name as locationName, 'hotel' AS locationType, IFNULL(hotel.address, '') as locationDetails
        FROM `tabHotel` as hotel
        INNER JOIN `tabArea` as area ON hotel.area=area.name
        INNER JOIN `tabTown` as town ON area.town=town.name
        WHERE hotel.hotel_name LIKE %(txt)s or area.area_name LIKE %(txt)s or town.town_name LIKE %(txt)s and hotel.disabled=0
        ORDER BY 
			if(locate(%(_txt)s, hotel.name), locate(%(_txt)s, hotel.name), 99999),
			if(locate(%(_txt)s, hotel.hotel_name), locate(%(_txt)s, hotel.hotel_name), 99999)
		LIMIT {page_len} OFFSET {start}
		)
	""".format(page_len=page_len, start=start),{"txt": "%%%s%%" % search, '_txt': search}, as_dict=True)
	return hotels


@frappe.whitelist(allow_guest=True)
def get_transfer_locations(search="", start=0, page_len=10):
	hotels = frappe.db.sql("""
		(SELECT air.name as locationId, air.airport_name as locationName, 'airport' AS locationType, 'Airport' as locationDetails
        FROM `tabAirport` as air
        WHERE air.airport_name LIKE %(txt)s AND air.portal_disabled=0
						)
        UNION
        (SELECT area.name as locationId, area.area_name as locationName, 'area' AS locationType,CONCAT(area.city, ", ", area.town)  AS locationDetails
        FROM `tabArea` as area
		INNER JOIN `tabTown` as town ON area.town=town.name
        WHERE area.area_name LIKE %(txt)s or town.town_name LIKE %(txt)s AND area.portal_disabled=0
        ORDER BY 
			if(locate(%(_txt)s, area.name), locate(%(_txt)s, area.name), 99999),
			if(locate(%(_txt)s, area.area_name), locate(%(_txt)s, area.area_name), 99999)
		LIMIT {page_len} OFFSET {start})
        UNION
		(
        SELECT hotel.name as locationId, hotel.hotel_name as locationName, 'hotel' AS locationType, IFNULL(hotel.address, '') as locationDetails
        FROM `tabHotel` as hotel
        INNER JOIN `tabArea` as area ON hotel.area=area.name
        INNER JOIN `tabTown` as town ON area.town=town.name
        WHERE hotel.hotel_name LIKE %(txt)s or area.area_name LIKE %(txt)s or town.town_name LIKE %(txt)s AND hotel.disabled=0
        ORDER BY 
            if(locate(%(_txt)s, hotel.name), locate(%(_txt)s, hotel.name), 99999),
            if(locate(%(_txt)s, hotel.hotel_name), locate(%(_txt)s, hotel.hotel_name), 99999)
		LIMIT {page_len} OFFSET {start}
				)
	""".format(page_len=page_len, start=start),{"txt": "%%%s%%" % search, '_txt': search}, as_dict=True)
	return hotels


@frappe.whitelist(allow_guest=True)
def get_nationalities(search="", start=0, page_len=10):
	hotels = frappe.db.sql("""
		SELECT name, nationality_name as nationality
        FROM `tabNationality`
        WHERE nationality_name LIKE %(txt)s
		LIMIT {page_len} OFFSET {start}
	""".format(page_len=page_len, start=start),{"txt": "%%%s%%" % search}, as_dict=True)
	return hotels
