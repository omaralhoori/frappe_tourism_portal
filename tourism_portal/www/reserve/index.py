import frappe
from frappe import _
import json

from tourism_portal.api.reserve import get_invoice_data

no_cache = 1
def get_context(context):
    context.no_cache = True
    if frappe.session.user == "Guest":
        frappe.throw(_("Log in to access this page."), frappe.PermissionError)
    invoice = frappe.form_dict.invoice
    context.invoice_details = get_invoice_data(invoice)
    # params = frappe.form_dict.params
    # params = json.loads(params)
    # rooms = json.loads(frappe.form_dict.rooms)

    # if not rooms.get('hotel'): frappe.throw(_('Please Select Hotel'))
    # hotel_id = rooms.pop('hotel')
    # all_reserved_rooms = {}
    
    # for room in rooms:
    #     reserved_rooms = []
    #     # split room names
    #     room_names = room.split('-')
    #     # get all reserverd rooms
    #     for rr in rooms[room]:
    #         if rooms[room][rr] > 0:
    #             rm = [rr] * rooms[room][rr]
    #             reserved_rooms.extend(rm)    
    #     if len(room_names ) != len(reserved_rooms):
    #         frappe.throw(_('Selected rooms are not correct'))
    #     for rn, rz in zip(room_names, reserved_rooms):
    #         all_reserved_rooms[rn] = rz
    
    # for hotel in params:
    #     for pax in hotel.get('paxInfo'):
    #         if not all_reserved_rooms.get(pax.get('roomName')):
    #             frappe.throw(_('You did not select all rooms'))
    #         pax['reserved_room'] = all_reserved_rooms.get(pax.get('roomName'))
    #     hotel['hotel_name'] = frappe.db.get_value("Hotel", hotel_id, "hotel_name")
    # context.reservation_details = params