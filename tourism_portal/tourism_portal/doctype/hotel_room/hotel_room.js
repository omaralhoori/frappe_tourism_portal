// Copyright (c) 2023, omaralhoori and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hotel Room', {
	refresh: function(frm) {
		if (!frm.is_new()){
			frm.add_custom_button(__('Add Room Contract'), function(){
				frm.events.add_room_contract(frm);
			});
			frm.add_custom_button(__('View All Contracts'), function(){
				frm.events.view_all_contracts(frm);
			});
		}
		frm.events.render_images(frm);
	},
	add_room_contract(frm) {
		frappe.new_doc('Hotel Room Contract', {
			hotel: frm.doc.hotel,
			room_type: frm.doc.room_type
		})
	},
	view_all_contracts(frm){
		frappe.route_options = {'hotel': frm.doc.hotel, "room_type": frm.doc.room_type};
			frappe.set_route('List', 'Hotel Room Contract');
	},
	render_images(frm){
		let attachments = frm.attachments.get_attachments();
		let image_extensions = ['png', 'jpe', 'jpg', 'jpeg', 'bmp', 'jfif', 'tiff', 'gif'];
		$(frm.fields_dict.images.wrapper).html('')
		for (let i in attachments){
			let attachment = attachments[i];
			let fname = attachment.file_name.split('.')
			if (image_extensions.includes(fname[fname.length - 1].toLowerCase())){
				$(`<div class="image-card">
					<div class="card-body"> 
					<img src="${attachment.file_url}"/>
					</div>
				</div>`).appendTo(frm.fields_dict.images.wrapper)
			}
		}
	},
});
