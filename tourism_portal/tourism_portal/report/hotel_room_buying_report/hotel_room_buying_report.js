// Copyright (c) 2023, omaralhoori and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Hotel Room Buying Report"] = {
	"filters": [
		{
			"fieldname":"hotel",
			"label": __("Hotel"),
			"fieldtype": "Link",
			"options": "Hotel",
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
	]
};
