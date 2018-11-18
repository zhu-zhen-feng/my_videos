var imageCodeId = ""

// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    // 浏览器要发起图片验证码请求/image_code?imageCodeId=xxxxx
    imageCodeId = generateUUID()
    // 生成 url
    var url = "/passport/image_code?imageCodeId=" + imageCodeId
    // 给指定img标签设置src,设置了地址之后，img标签就会去向这个地址发起请求，请求图片
    $(".get_pic_code").attr("src", url)
}

function logOut() {
    $.get('/passport/logout', function (resp) {
        location.reload()
    })
}

// 调用该函数模拟点击左侧按钮
function fnChangeMenu(n) {
    var $li = $('.option_list li');
    if (n >= 0) {
        $li.eq(n).addClass('active').siblings().removeClass('active');
        // 执行 a 标签的点击事件
        $li.eq(n).find('a')[0].click()
    }
}

// 一般页面的iframe的高度是660
// 新闻发布页面iframe的高度是900
function fnSetIframeHeight(num){
	var $frame = $('#main_frame');
	$frame.css({'height':num});
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}


$(function(){
    // 搜索栏的提交
    $(".search").submit(function (e){
        e.preventDefault()
        var keywords = $(".search #keywords").val()
        if (!keywords) {
            return;
        }
         $.get("/search?keywords="+ keywords, function (resp) {
        // 数据加载完毕，设置【正在加载数据】的变量为 false 代表当前没有在加载数据
        data_querying = false
        if (resp.errno == "0") {
            // 给总页数据赋值
            // 清除已有数据
            $(".list_con").html("")

            // 添加请求成功之后返回的数据

            // 显示数据
            for (var i=0;i<resp.data.video_dict_li.length;i++) {
                var video = resp.data.video_dict_li[i]
                var content = '<li>'
                content += '<a href="/videos/' + video.id + '" class="video_pic fr"><img src="' + video.img_url + '?imageView2/1/w/220/h/170"></a>'
                content += '<div class="con_box"><a href="/videos/'+ video.id+'"><h3>'+ video.intro+'</h3></a>'
                content += '<span>永胜学院&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>'
                content += '<span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;播放次数：'+ video.clicks+'</span></div>'
                // content += '</div>'
                // content += '</li>'
                $(".list_con").append(content)
            }
        }else {
            // 请求失败
            console.log(resp.errmsg)
        }
    })
    })
	// 打开登录框
	$('.login_btn').click(function(){
        $('.login_form_con').show();
	})
	
	// 点击关闭按钮关闭登录框或者注册框
	$('.shutoff').click(function(){
		$(this).closest('form').hide();
	})

    // 隐藏错误
    $(".login_form #mobile").focus(function(){
    $("#login-mobile-err").hide();
    });
	$(".login_form #password").focus(function(){
    $("#login-password-err").hide();
    });
    $(".login_form #register_user").focus(function(){
    $("#register-user-err").hide();
    });
    $(".login_form #register_mobile").focus(function(){
        $("#register-mobile-err").hide();
    });
    $(".login_form #register_password").focus(function(){
        $("#register-password-err").hide();
    });
    $(".register_form #imagecode").focus(function(){
        $("#register-image-code-err").hide();
    });

	// 点击输入框，提示文字上移
	// $('.form_group').on('click focusin',function(){
	// 	$(this).children('.input_tip').animate({'top':-5,'font-size':12},'fast').siblings('input').focus().parent().addClass('hotline');
	// })

    $('.form_group').on('click',function(){
        $(this).children('input').focus()
    })

    $('.form_group input').on('focusin',function(){
        $(this).siblings('.input_tip').animate({'top':-5,'font-size':12},'fast')
        $(this).parent().addClass('hotline');
    })

	// 输入框失去焦点，如果输入框为空，则提示文字下移
	$('.form_group input').on('blur focusout',function(){
		$(this).parent().removeClass('hotline');
		var val = $(this).val();
		if(val=='')
		{
			$(this).siblings('.input_tip').animate({'top':22,'font-size':14},'fast');
		}
	})


	// 打开注册框
	$('.register_btn').click(function(){
		$('.register_form_con').show();
		generateImageCode()
	})


	// 登录框和注册框切换
	$('.to_register').click(function(){
		$('.login_form_con').hide();
		$('.register_form_con').show();
        generateImageCode()
	})

	// 登录框和注册框切换
	$('.to_login').click(function(){
		$('.login_form_con').show();
		$('.register_form_con').hide();
	})

	// 根据地址栏的hash值来显示用户中心对应的菜单
	var sHash = window.location.hash;
	if(sHash!=''){
		var sId = sHash.substring(1);
		var oNow = $('.'+sId);		
		var iNowIndex = oNow.index();
		$('.option_list li').eq(iNowIndex).addClass('active').siblings().removeClass('active');
		oNow.show().siblings().hide();
	}

	// 用户中心菜单切换
	var $li = $('.option_list li');
	var $frame = $('#main_frame');

	$li.click(function(){
		if($(this).index()==5){
			$('#main_frame').css({'height':900});
		}
		else{
			$('#main_frame').css({'height':660});
		}
		$(this).addClass('active').siblings().removeClass('active');
		$(this).find('a')[0].click()
	})

    // 登录表单提交
    $(".login_form_con").submit(function (e) {
        e.preventDefault()
        var mobile = $(".login_form #mobile").val()
        var password = $(".login_form #password").val()

        if (!mobile) {
            $("#login-mobile-err").show();
            return;
        }

        if (!password) {
            $("#login-password-err").show();
            return;
        }

        // 发起登录请求
        var params = {
            "mobile": mobile,
            "password": password
        }
        
        $.ajax({
            url: "/passport/login",
            type: "post",
            contentType: "application/json",
            // 在 header 中添加 csrf_token 的随机值
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    // 代表登录成功
                    location.reload()
                }else {
                    console.log(resp.errmsg)
                    $("#login-password-err").html(resp.errmsg)
                    $("#login-password-err").show()
                }
            }
        })


    })


    //注册按钮点击
    $(".register_form_con").submit(function (e) {
        // 阻止默认表单提交操作
        e.preventDefault()

        // 取到用户输入的内容
        var nickname = $("#register_user").val()
        var mobile = $("#register_mobile").val()
        var imageCode = $("#imagecode").val();
        var password = $("#register_password").val()
        if (!nickname) {
            $("#register-user-err").show();
            return;
        }
		if (!mobile) {
            $("#register-mobile-err").show();
            return;
        }
        if (!imageCode){
            $("#image-code-err").show();
            return;
        }
        if (!password) {
            $("#register-password-err").html("请填写密码!");
            $("#register-password-err").show();
            return;
        }

		if (password.length < 6) {
            $("#register-password-err").html("密码长度不能少于6位");
            $("#register-password-err").show();
            return;
        }

        // 准备参数
        var params = {
            "nickname":nickname,
            "mobile": mobile,
            "img_code": imageCode,
            "img_code_id":imageCodeId,
            "password": password
        }
        $.ajax({
            url: "/passport/register",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    // 代表注册成功就代表登录成功
                    location.reload()
                }else {
                    // 代表注册失败
                    $("#register-password-err").html(resp.errmsg)
                    $("#register-password-err").show()
                }
            }
        })


    })
})

