
$(document).ready(function(){
	$.urlParam = function(name){
		var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
		if (results===null){
			return null;
		}
		else{
			return decodeURI(results[1]) || 0;
		}
	};
	$.ajax({
		type:"POST",
		url:"authcheck"
	}).done(function(out) {
		if(out=="True"){
			$("#login-link").hide();
			$("#account-link").show();
			$("#hidden-pages").show();
		}
	})
	$("#logout").click(function(){
		$.ajax({
			type: "POST",
			url:"logout",
			dataType: "text"
		}).done(function(out) {
			if(out == "0"){
				//$("#logout-message").text("You are now logged out");
				//$("#logout-message").show();
				toastr.info("You are now logged out");
				$("#login-link").show();
				$("#account-link").hide();
				setTimeout(function(){window.location.replace("/");}, 1000);
			}
		})
	});
	toastr.options = {
	  "closeButton": true,
	  "debug": false,
	  "newestOnTop": false,
	  "progressBar": false,
	  "positionClass": "toast-bottom-right",
	  "preventDuplicates": false,
	  "onclick": null,
	  "showDuration": "300",
	  "hideDuration": "1000",
	  "timeOut": "5000",
	  "extendedTimeOut": "1000",
	  "showEasing": "swing",
	  "hideEasing": "linear",
	  "showMethod": "fadeIn",
	  "hideMethod": "fadeOut"

	};

	//toastr.info("Output", "");
})