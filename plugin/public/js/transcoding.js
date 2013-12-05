// VuPlus Port Jumper 
// 2012.12.10
function getWinSize(win) {
	if(!win) win = window;
	var s = {};
	if(typeof win.innerWidth != "undefined") {
		s.screenWidth = win.screen.width;
		s.screenHeight = win.screen.height;
	} else {
		s.screenWidth = 0;
		s.screenHeight = 0;
	}
	return s;
}

function getDeviceType() {
	var ss = getWinSize();
	var screenLen = 0;

	if( ss.screenHeight > ss.screenWdith ) {
		screenLen = ss.screenHeight;
	} else {
		screenLen = ss.screenWidth;
	}

	if( screenLen < 500 ) {
		return "phone";
	} else {
		return "tab";
	}
}

function getOSType() {
	var agentStr = navigator.userAgent;

	if(agentStr.indexOf("iPod") > -1 || agentStr.indexOf("iPhone") > -1)
		return "ios";
	else if(agentStr.indexOf("Android") > -1)
		return "android";
	else
		return "unknown";
}

function jumper80( file ) {
	var deviceType = getDeviceType();
	document.portFormTs.file.value = file;
	document.portFormTs.device.value = "etc";
	document.portFormTs.submit();
}

function jumper8003( file ) {
	var deviceType = getDeviceType();
	document.portFormTs.file.value = file;
	document.portFormTs.device.value = "phone";
	document.portFormTs.submit();
}

function jumper8002( sref, sname ) {
	var deviceType = getDeviceType();
	document.portForm.ref.value = sref;
	document.portForm.name.value = sname;
	document.portForm.device.value = "phone";
	document.portForm.submit();
}

function jumper8001( sref, sname ) {
	var deviceType = getDeviceType();
	document.portForm.ref.value = sref;
	document.portForm.name.value = sname;
	document.portForm.device.value = "etc";
	document.portForm.submit();
}
