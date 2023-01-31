function manage_footer() {
    if ($(document).height() == $(window).height()) {
        $('footer').addClass('fixed-bottom');
        $('#footer-helper').height($('footer').height());
    } else {
        $('footer').removeClass('fixed-bottom');
        $('#footer-helper').height('0px');
    }
}
async function add_views(){
    path=window.location.pathname
    await $.ajax({
        url: `https://api.countapi.xyz/hit${path}/visits`,
        success: async function(r,s){
            let view_html = `<i class="far fa-eye"></i> ${r['value']}`
            $('#views-section').html(view_html)
        },
        error: function(e,s){
            let view_html = `<i class="far fa-eye"></i> 99999`
            $('#views-section').html(view_html)
        },
    })
}
add_views()
manage_footer()
window.addEventListener('resize', manage_footer, true);
$('.btn-close').click(() => {setTimeout(manage_footer, 200)})
function random(){return (Math.random() + 1).toString(36).substring(2);}
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
async function submit_tag() {
    question=$('#question').val()
    if(question==''){show_msg('warning', 'Please enter a sentence first.');return false}
    $("#tag-submit").attr("disabled", "true")
    await $.ajax({
        url: '/api/solve-tag',
        type:'POST',
        data:'question='+encodeURIComponent(question),
        headers:{'Content-Type':'application/x-www-form-urlencoded'},
        success: async function(r,s){
            if(! r['success']){
                show_msg('danger', 'Something went wrong with the server. Please check your sentence or try again later. Error: '+ r["error"])
            } else{
                add_answer(r['question'], r['answer']);
                $("#question").val('').removeClass('active');
            }
            $("#tag-submit").removeAttr("disabled")
        },
        error: function(e,s){
            show_msg('danger', 'Something went wrong with the server. Please try again later.')
            $("#tag-submit").removeAttr("disabled")
        },
    });$("#tag-submit").removeAttr("disabled")
}
function add_answer(question, answer){
    class_name=random()
    old_html=$('#answers').html();
    new_html=`<div class="card ${class_name} my-3"><div class="card-body"><p class="card-text">${question}, <u>${answer}</u>?</p></div></div>`
    $('#answers').html(new_html + old_html);
    window.scrollTo(0,$(`.${class_name}`).offset().top - 200);
    setTimeout(function(){$(`.${class_name}`).css('box-shadow','0 8px 17px 0 rgba(0,0,0,.2),0 6px 20px 0 rgba(0,0,0,.19)')}, 300);
}
