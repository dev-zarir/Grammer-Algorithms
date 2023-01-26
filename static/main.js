function manage_footer() {
    if ($(document).height() == $(window).height()) {
        $('footer').addClass('fixed-bottom');
        $('#footer-helper').height($('footer').height());
    } else {
        $('footer').removeClass('fixed-bottom');
        $('#footer-helper').height('0px');
    }
}
manage_footer()
window.addEventListener('resize', manage_footer, true);
$('.btn-close').click(() => {setTimeout(manage_footer, 200)})

function show_msg(type, msg) {
    if(type=='primary'){icon='fa-info-circle'}
    else if(type=='info'){icon='fa-chevron-circle-right'}
    else if(type=='success'){icon='fa-check-circle'}
    else if(type=='warning'){icon='fa-exclamation-triangle'}
    else if(type=='danger'){icon='fa-times-circle'}
    else {icon='fa-gem'}
    msg_html=`<div class="alert alert-${type} alert-dismissible fade show" role="alert"><i class="fas ${icon} me-3"></i>${msg}<button class="btn-close" data-mdb-dismiss="alert" aria-label="Close"></button></div>`
    old_html=$('#alerts').html()
    $('#alerts').html(old_html + msg_html)
    window.scrollTo(0,$("#alerts").offset().top - 100)
}
function clear_msg(){
    $('#alerts').html('');
}