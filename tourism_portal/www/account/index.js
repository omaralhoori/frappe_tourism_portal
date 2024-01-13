function userModalSubmitted(e){
    e.preventDefault();
    var form = $(this).closest('form');
    var url = form.attr('action');
    var data = form.serialize();
    console.log(data);
}