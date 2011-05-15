function blocklink() {
	$("#osm-dijkstra").click(function () {
		window.location.href = "/osm-dijkstra";
	});
	$("#mtc-dijkstra").click(function () {
		window.location.href = "/mtc-dijkstra";
	});
}

$(document).ready(function () {
	blocklink();
});
