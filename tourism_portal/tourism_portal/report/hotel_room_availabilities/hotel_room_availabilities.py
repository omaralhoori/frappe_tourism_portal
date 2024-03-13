# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime

def execute(filters=None):
	columns, data = [], []
	data, dates = get_data(filters)
	columns = get_columns(dates, filters)
	return columns, data

def get_columns(dates, filters={}):
	columns =  [
		{
            'fieldname': 'hotel',
            'label': _('Hotel'),
            'fieldtype': 'Link',
            'options': 'Hotel'
        },
		{
            'fieldname': 'contract_no',
            'label': _('Contract No'),
            'fieldtype': 'Link',
            'options': 'Hotel Room Contract'
        },
		{
            'fieldname': 'room_type',
            'label': _('Room Type'),
            'fieldtype': 'Data',
        },

	]

	dates_columns = [{"fieldname": date, "label": date, "fieldtype": "Data"} for date in dates]
	columns.extend(dates_columns)
	return columns
def get_data(filters={}):
	condations = "1"
	if filters.get('hotel'):
		condations += " AND tbl2.hotel=%(hotel)s"
	if filters.get('from_date'):
		condations += " AND tbl1.date>=%(from_date)s"
	if filters.get('to_date'):
		condations += " AND tbl1.date<=%(to_date)s"
	
	data = frappe.db.sql("""
		SELECT 
			tbl2.hotel, tbl2.room_type, tbl1.contract_no, 
			GROUP_CONCAT(tbl1.date) as dates,
			GROUP_CONCAT(
					  IF (
					  (tbl2.release_days =0 or DATEDIFF(tbl1.date, now()) > tbl2.release_days )
					   ,tbl1.available_qty, 0)) as qtys 
		FROM `tabRoom Availability` as tbl1
		INNER JOIN `tabHotel Room Contract` as tbl2 on tbl1.contract_no=tbl2.name
		WHERE {condations}
		GROUP BY tbl1.contract_no
	""".format(condations=condations), {**filters},as_dict=True)
	all_dates = []
	for item in data:
		dates = item['dates'].split(',')
		qtys = item['qtys'].split(',')
		for date, qty in zip(dates, qtys):
			item[date] = qty
		all_dates.extend(dates)
	all_dates = list(set(all_dates))
	# Convert date strings to datetime objects
	dates = [datetime.strptime(date, "%Y-%m-%d") for date in all_dates]
	
	# Sort the datetime objects
	sorted_dates = sorted(dates)
	sorted_date_strings = [date.strftime("%Y-%m-%d") for date in sorted_dates]
	return data, sorted_date_strings