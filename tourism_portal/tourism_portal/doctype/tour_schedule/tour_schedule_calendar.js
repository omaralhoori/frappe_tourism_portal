frappe.views.calendar["Tour Schedule"] = {
	field_map: {
        "start": "schedule_date",
		"end": "schedule_date",
		"id": "name",
        "title": "tour_type",
        "allDay": "allDay",

	},
	gantt: false,
	order_by: "schedule_date",
	filters: [
		{
			"fieldtype": "Link",
			"fieldname": "tour_type",
			"options": "Tour Type",
			"label": __("Tour Type")
		},
		{
			"fieldtype": "Link",
			"fieldname": "city",
			"options": "City",
			"label": __("City")
		},
	],
    get_events_method: "frappe.desk.calendar.get_events",
}