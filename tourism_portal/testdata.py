import frappe



def create_hotels(hotel_count=10):
    areas = frappe.db.get_all("Area", {"portal_disabled": 0})
    for _count in range(hotel_count):
        hotel = frappe.get_doc({
            "doctype": "Hotel",
            "hotel_code": f"HTL{_count}",
            "hotel_name": f"Hotel {_count}",
            "hotel_description": f"Hotel {_count} description",
            "hotel_address": f"Hotel {_count} address",
            "area": areas[_count].name,
        })
        hotel.insert(ignore_permissions=True)
        create_hotel_room(hotel.name, "STD", "SGL")
        create_hotel_room(hotel.name, "STD", "DBL")
        create_hotel_room(hotel.name, "STD", "TRPL")
    frappe.db.commit()
def create_hotel_room(hotel, room_type, room_acmnd_type):
    room = frappe.get_doc({
        "doctype": "Hotel Room",
        "hotel": hotel,
        "room_type": room_type,
        "room_accommodation_type": room_acmnd_type,
    })
    room.insert(ignore_permissions=True)
    return room