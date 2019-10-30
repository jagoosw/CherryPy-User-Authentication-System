$.urlParam = function(name){
	var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
	if (results==null){
		return null;
	}
	else{
		return decodeURI(results[1]) || 0;
	}
}
$(document).ready(function(){
	$("#logout").click(function(){
		$.ajax({
			type: "POST",
			url:"logout",
			dataType: "text"
		}).done(function(out) {
			if(out == "0"){
				$("#logout-message").text("You are now logged out");
				$("#logout-message").show();
				$("#login-link").show();
				$("#account-link").hide();
			}
		})
	});
	$.ajax({
			type:"POST",
			url:"authenticated"
	}).done(function(out) {
		if(out=="True"){
			$("#login-link").hide();
			$("#account-link").show();
		}
		else{
			$("#buttons").hide();
			$("#title").text("You are not logged in, please sign in before you can view this page")
		}
	})
	$("#show-email").click(function(){
		$("#buttons").hide()
		$("#back").show()
		$("#email-form").show()
		$("#current-password-form").show()
	})
	$("#show-password").click(function(){
		$("#buttons").hide()
		$("#back").show()
		$("#password-form").show()
		$("#current-password-form").show()
	})
	$("#back").click(function(){
		$("#buttons").show()
		$("#password-form").hide()
		$("#email-form").hide()
		$("#current-password-form").hide()
		$("#back").hide()
	})

	$("#submit-password").click(function(){
		$.ajax({
			type: "POST",
			url:"changepassword",
			data: {"password": $("input[name='current-password']").val(), "new_password": $("input[name='new-password']").val(), "new_password_conf": $("input[name='new-password-conf']").val()},
			dataType: "text"
		}).done(function(out) {
			if(out == 0){
				$("#current-password-form").hide();
				$("#password-form").hide();
				toastr.info("Password change successful", "");
			}
			else {
				toastr.info(out);
			}
		})
	})

	$("#submit-email").click(function(){
		$.ajax({
			type: "POST",
			url:"changeemail",
			data: {"password": $("input[name='current-password']").val(), "new_email": $("input[name='new-email']").val(), "new_email_conf": $("input[name='new-email-conf']").val()},
			dataType: "text"
		}).done(function(out) {
			if(out == 0){
				$("#current-password-form").hide();
				$("#email-form").hide();
				toastr.info("Email change successful");
			}
			else {
				toastr.info(out);
			}
		})
	})

})