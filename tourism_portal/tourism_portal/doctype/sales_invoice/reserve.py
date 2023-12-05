import frappe


def add_rooms_to_invoice(invoice, rooms):
    for searchName in rooms:
        search = rooms[searchName]
        for roomName in search:
            room = rooms[searchName][roomName]
            invc_room = invoice.append("rooms")
            invc_room.room = room['room_id']
            invc_room.hotel_search = searchName
            invc_room.room_name = roomName#room['room_name']
            invc_room.nationality = room.get('nationality')
            invc_room.check_in = room.get('check_in')
            invc_room.check_out = room.get('check_out')
            total_price = 0
            for i in range(int(room['pax_info'].get('adults'))):
                guest = invoice.append("room_pax_info")
                guest.room_name = roomName#room['room_name']
                guest.hotel_search = searchName
                guest.guest_type = 'Adult'
            for child_age in room['pax_info'].get('childrenInfo'):
                guest = invoice.append("room_pax_info")
                guest.guest_type = 'Child'
                guest.hotel_search = searchName
                guest.room_name = roomName#room['room_name']
                guest.guest_age = int(child_age)
            for contract in room['contracts']:
                room_price = invoice.append('room_price')
                room_price.room_name=  roomName
                room_price.hotel_search = searchName
                room_price.check_in = contract['check_in']
                room_price.check_out = contract['check_out']
                room_price.nights = frappe.utils.date_diff(room_price.check_out, room_price.check_in)
                room_price.selling_price = float(contract['price']) / room_price.nights
                room_price.total_selling_price = float(contract['price'])
                total_price += float(contract['price'])
                room_price.contract_id = contract.get('contract_id')
                room_price.contract_price = contract.get('price_id')
                room_price.inquiry_id = contract.get('inquiry_id')
                if room_price.contract_price:
                    room_price.buying_currency,room_price.buying_price = frappe.db.get_value("Hotel Room Price", room_price.contract_price,["buying_currency", "buying_price"])
                elif room_price.inquiry_id:
                    room_price.buying_currency,room_price.buying_price = frappe.db.get_value("Hotel Inquiry Request", room_price.inquiry_id,["buying_currency", "buying_price"])
                if room_price.contract_id:
                    room_price.cancellation_policy = frappe.db.get_value("Hotel Room Contract",room_price.contract_id, "cancellation_policy" )
                if not room_price.cancellation_policy:
                    hotel = frappe.db.get_value("Hotel Room",  room['room_id'], "hotel", cache=True)
                    room_price.cancellation_policy = frappe.db.get_value("Hotel", hotel, "hotel_cancellation_policy")
            invc_room.total_price = total_price
    

def add_transfers_to_invoice(invoice, transfers):
    for searchName in transfers:
        search = transfers[searchName]
        for transferName in search:
            transfer = transfers[searchName][transferName]
            invc_transfer = invoice.append("transfers")
            invc_transfer.transfer_search = searchName
            invc_transfer.transfer_name = transferName
            invc_transfer.transfer_type = transfer['transfer_type']
            invc_transfer.transfer = transfer['transfer_id']
            invc_transfer.transfer_price = transfer['transfer_price']
            invc_transfer.adults = transfer['pax_info'].get('adults')
            invc_transfer.children = transfer['pax_info'].get('children')
            invc_transfer.pick_up = transfer['pick_up']
            invc_transfer.pick_up_type = transfer['pick_up_type']
            invc_transfer.pick_up_postal_code = transfer['pick_up_postal_code']
            invc_transfer.transfer_date = transfer['transfer_date']
            invc_transfer.drop_off = transfer['drop_off']
            invc_transfer.drop_off_type = transfer['drop_off_type']
            invc_transfer.drop_off_postal_code = transfer['drop_off_postal_code']
            invc_transfer.flight_no = transfer.get('flight_no')
            for i in range(int(transfer['pax_info'].get('adults'))):
                    guest = invoice.append("transfer_pax_info")
                    guest.transfer_name = transferName
                    guest.transfer_search = searchName
                    guest.guest_type = 'Adult'
            for child_age in transfer['pax_info'].get('childrenInfo'):
                guest = invoice.append("transfer_pax_info")
                guest.guest_type = 'Child'
                guest.transfer_search = searchName
                guest.transfer_name = transferName
                guest.guest_age = int(child_age)