import frappe
from frappe import _
import json

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    params = frappe.form_dict.params
    params = json.loads(params)
    rooms = json.loads(frappe.form_dict.rooms)
    print(rooms)
    all_reserved_rooms = {}
    
    for room in rooms:
        reserved_rooms = []
        # split room names
        room_names = room.split('-')
        # get all reserverd rooms
        for rr in rooms[room]:
            if rooms[room][rr] > 0:
                rm = [rr] * rooms[room][rr]
                reserved_rooms.extend(rm)    
        if len(room_names ) != len(reserved_rooms):
            frappe.throw(_('Selected rooms are not correct'))
        for rn, rz in zip(room_names, reserved_rooms):
            all_reserved_rooms[rn] = rz
    
    for hotel in params:
        for pax in hotel.get('paxInfo'):
            if not all_reserved_rooms.get(pax.get('roomName')):
                frappe.throw(_('You did not select all rooms'))
            pax['reserved_room'] = all_reserved_rooms.get(pax.get('roomName'))

    context.reservation_details = params