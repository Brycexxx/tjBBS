$(document).ready(function () {
    $("#give-comment").click(function () {
        //let a = $("input").offset().top;
        //$("html, body").animate({scrollTop: a}, 'slow');
        window.scrollTo(0, document.documentElement.scrollHeight-document.documentElement.clientHeight);
    });
});
$(document).ready(function () {
    $(".do_reply").click(function (e) {
        sp = e.target;
        const reply = $(sp).next().next();
        $(reply).toggle();
    });
});

/*
function reply(e){
    const span = e.target;
    const div = span.nextSibling.nextSibling;
    div.css('display', 'block');
}

*/