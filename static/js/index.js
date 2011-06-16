function blocklink() {
	$("#osm-dijkstra").click(function () {
		window.location.href = "/osm-dijkstra";
	});
	$("#mtc-dijkstra").click(function () {
		window.location.href = "/mtc-dijkstra";
	});
	$("#mtc-nonsc").click(function () {
		window.location.href = "/mtc-nonsc";
	});
}

$(document).ready(function () {
	blocklink();
});
