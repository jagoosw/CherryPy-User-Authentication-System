$(document).ready(function(){
	if ($.urlParam('confirm')=="0"){
		$("#buttons").hide();
		$("#title").text("Email Confirmation");
		$.ajax({
			type: "POST",
			url:"confirm",
			data: {"id": $.urlParam('id'), "confirm": $.urlParam('string')},
			dataType: "text"
		}).done(function(out) {
			toastr.info(out);
			$("#output-message").show();
			$("#output-message").text(out);
		});
  	}

	$.ajax({
		type:"POST",
		url:"authcheck"
	}).done(function(out) {
		if(out=="True"){
			$("#login-link").hide();
			$("#account-link").show();
		}
	})

	$.ajax({
		type:"POST",
		url:"authenticated"
	}).done(function(out) {
		if(out=="True"){
			$("#buttons").hide();
			$("#title").text("You are already logged in")
		}
	})

	$("#logout").click(function(){
		$.ajax({
			type: "POST",
			url:"logout",
			dataType: "text"
		}).done(function(out) {
			if(out == "0"){
				$("#logout-message").text("You are now logged out");
				$("#logout-message").show();
				setTimeout(function(){window.location.replace("/");;}, 1000);
			}
		})
	});

	$("#show-login").click(function(){
		$("#login-form").show();
		$("#buttons").hide();
		$("#title").text("Login")
		$("#back").show();
	});

	$("#show-signup").click(function(){
		$("#signup-form").show();
		$("#title").text("Signup")
		$("#buttons").hide();
		$("#back").show();
	});

	$("#back").click(function(){
		$("#buttons").show();
		$("#login-form").hide();
		$("#signup-form").hide();
		$("#back").hide();
	});

	$("#submit-login").click(function(){
		toastr.info("Trying...");
		$.ajax({
			type: "POST",
			url:"login",
			data: {"email": $("input[name='login-email']").val(), "password": $("input[name='login-password']").val()},
			dataType: "text"
		}).done(function(out) {
			if(out == 0){
				$("#login-form").hide();
				toastr.info("Login success");
				$("#login-link").hide();
				$("#account-link").show();
				$("#hidden-pages").show
				$("#back").hide();
				$("#output-message").show();
				$("#output-message").text("Login successful");

			}
			else {
				toastr.info(out);
			}
		})
	});

	$("#show-reset").click(function(){
		$("#login-form").hide();
		$("#back").hide();
		$("#reset-form").show();
		$("#title").text("Reset Password")
	});

	$("#reset-back").click(function(){
	 $("#login-form").show();
	 $("#back").show();
	 $("#reset-form").hide();
	 $("#title").text("Login")
	});

	$("#submit-reset").click(function(){
		$.ajax({
			type: "POST",
			url:"reset",
			data: {"email": $("input[name='reset-email']").val()},
			dataType: "json"
		}).done(function(out) {
			if(out.status == "0"){
				$("#reset-2").show();
				$("#submit-reset").hide();
				$("#reset-start").hide();
			}
			else {
				toastr.info(out.status);
			}
		})
	});
	$("#submit-reset-1").click(function(){
		$.ajax({
			type: "POST",
			url:"reset",
			data: {"email": $("input[name='reset-email']").val()},
			dataType: "json"
		}).done(function(out) {
			if(out.status == "0"){
				$("#reset-2").hide();
				$("#reset-final").show();
			}
			else {
				toastr.info(out.status);
			}
		})
	});

	$("#submit-reset-final").click(function(){
		$.ajax({
			type: "POST",
			url:"reset",
			data: {"email": $("input[name='reset-email']").val(), "string": $("input[name='reset-string']").val(), "password": $("input[name='reset-password']").val(), "password_conf": $("input[name='reset-password-conf']").val()},
			dataType: "json"
		}).done(function(out) {
			if(out.status == "0"){
				$("#reset-final").hide();
				toastr.info("Password reset successful, you are now logged in");
			}
			else {
				toastr.info(out.status);
			}
		})
	});

	$("#submit-signup").click(function(){
		toastr.info("Processing, please wait...");
		toastr.info("This may take a few moments...");
		toastr.info("Do not press submit again or close the page...");
		$.ajax({
			type: "POST",
			url:"signup",
			data: {"email": $("input[name='signup-email']").val(), "name": $("input[name='signup-name']").val(), "password": $("input[name='signup-password']").val(),"email_conf": $("input[name='signup-email-conf']").val(), "password_conf": $("input[name='signup-password-conf']").val()},
			dataType: "text"
		}).done(function(out) {
			if(out == 0){
				$("#signup-form").hide();
				toastr.info("Sign up successful, you can login now");
				$("#output-message").show();
				$("#output-message").text("You can now login");
			}
			else {
				toastr.info(out);
			}
		})
	});
});
