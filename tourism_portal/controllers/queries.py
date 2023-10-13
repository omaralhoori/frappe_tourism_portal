import frappe

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def hotel_room_type(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT tbl2.name, tbl2.room_type 
        FROM `tabHotel Room` as tbl1
        INNER JOIN `tabRoom Type` as tbl2 ON tbl1.room_type=tbl2.name
        WHERE tbl1.hotel=%(hotel)s AND (tbl2.name LIKE %(txt)s
                OR tbl2.room_type LIKE %(txt)s)
        GROUP BY tbl2.name
        ORDER BY
            IF(LOCATE(%(_txt)s, tbl2.name), LOCATE(%(_txt)s, tbl2.name), 99999),
            IF(LOCATE(%(_txt)s, tbl2.room_type), LOCATE(%(_txt)s, tbl2.room_type), 99999),
            tbl2.name, tbl2.room_type
        LIMIT %(start)s, %(page_len)s
        
    """, {
        'txt': "%{}%".format(txt),
        '_txt': txt.replace("%", ""),
        'start': start,
        'page_len': page_len,
        'hotel': filters.get('hotel')
    })