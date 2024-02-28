$('.dropdown-toggle').click(function() {
    var dropdownMenu = $(this).next('.dropdown-menu');
    $(this).parent().toggleClass('show');
    dropdownMenu.toggleClass('show');

});

function toggleLoader(value){
    if (value){
        $('#loader').removeClass('d-none')
    }else{
        $('#loader').addClass('d-none')
    }
}

function throwError(message){
    toastr.error(message)
    throw message;
}