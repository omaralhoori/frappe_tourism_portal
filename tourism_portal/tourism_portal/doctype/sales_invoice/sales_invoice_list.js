frappe.listview_settings["Sales Invoice"] = {
	hide_name_column: true,
	add_fields: ["status"],
	get_indicator: function(doc) {
        if (doc.status=="Draft") {
			return [__("Draft"), "orange", "status,=,Draft"];
        }
        if (doc.status=="Submitted") {
			return [__("Completed"), "green", "status,=,Submitted"];
        }
        if (doc.status=="Cancelled") {
			return [__("Cancelled"), "red", "status,=,Cancelled"];
        }
    }
}