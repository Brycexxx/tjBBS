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
        const sp_value = $(sp).text();
        if (sp_value === "回复") {
            $(sp).html("收起回复");
        }
        else {
            $(sp).html("回复");
        }
        const reply = $(sp).next().next();
        $(reply).toggle();
    });
});

$(document).ready(function () {
   $("#only-owner").click(function (e) {
      $(".not-owner").toggle();
   });
});

$(document).ready(function () {
    $(".do_unfold").click(function (e) {
        const image_tag = e.target;
        const li_tag = $(image_tag).parent();
        const li_fold = $(li_tag).siblings(".display-form");
        $(li_fold).toggle();
    });
});
$(document).ready(function () {
    $(window).resize(function () {
        if ($(window).width() < 730) {
            $(".post-h3").css("display", "block");
            $(".float-right").css("float", "left")
        }
        else {
            $(".post-h3").css("display", "inline");
            $(".float-right").css("float", "right")
        }
    })
});
