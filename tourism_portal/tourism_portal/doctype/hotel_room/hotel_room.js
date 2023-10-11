// Copyright (c) 2023, omaralhoori and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hotel Room', {
	refresh: function(frm) {
		frm.events.render_images(frm);
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
