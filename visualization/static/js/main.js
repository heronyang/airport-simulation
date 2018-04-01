/* Map */
var map;
var nodes = [];
var links = [];

const FLIGT_ICON_URL = "/image/flight.png";
const GATE_ICON_URL = "http://maps.google.com/mapfiles/ms/icons/blue-dot.png";
const SPOT_ICON_URL = "http://maps.google.com/mapfiles/ms/icons/green-dot.png";

const PUSHBACK_WAY_COLOR = "#0000FF";   // blue
const TAXIWAY_COLOR = "#00FF00";    // green
const RUNWAY_COLOR = "#FF0000";    // red

const ZOOM_GLOBAL = 2;
const ZOOM_AIRPORT = 17;

function initMap() {
	map = new google.maps.Map(document.getElementById("map"), {
		center: {lat: 0, lng: 0},
		zoom: ZOOM_GLOBAL
	});
}

function resetMap(lat, lng, zoom) {
    var pos = new google.maps.LatLng(lat, lng);
    map.setOptions({
        center: pos,
        zoom: zoom
    });
}

function getParams() {
    var params = [], hash;
    var hashes = window.location.href
        .slice(window.location.href.indexOf("?") + 1)
        .split("&");
    for (var i = 0; i < hashes.length; i++) {
        hash = hashes[i].split("=");
        params.push(hash[0]);
        params[hash[0]] = hash[1];
    }
    return params;
}

function drawNode(lat, lng, icon_url, content) {

	var infowindow = new google.maps.InfoWindow({
		content: content
	});

    var marker = new google.maps.Marker({
        position: {lat: lat, lng: lng},
        map: map,
        icon: icon_url
    });

	marker.addListener("click", function() {
		infowindow.open(map, marker);
	});

    nodes.push(marker);

}

function drawLink(nodes, color) {
    link = new google.maps.Polyline({
        path: nodes,
        strokeColor: color,
    });
    link.setMap(map);
    links.push(link);
}

function removeAll() {
    for (var i = 0; i < nodes.length; i++) {
        nodes[i].setMap(null);
    }
    nodes = [];
    for (var i = 0; i < links.length; i++) {
        links[i].setMap(null);
    }
    links = [];
}

/* UI Callbacks */
$("#auto").click(function(e) {
    console.log("auto");
    e.preventDefault();
    toggleAutoRun();
});

$("#prev").click(function(e) {
    e.preventDefault();
    console.log("prev");
});

$("#next").click(function(e) {
    e.preventDefault();
    console.log("next");
});

/* UI Operations */
function loadPlans(plans) {
    var dropdown = $("#dropdown-plan");
    dropdown.empty();
    for (let plan of plans) {
        dropdown.append('<a class="dropdown-item option-plan" href="#">' +
            plan + '</a>');
    }
    $(".option-plan").click(function(e) {
        e.preventDefault();
        window.location.href = "?plan=" + e.target.text;
    });
}

function setPlanShow(plan) {
    $("#dropdown-plan-label").html(plan);
}

function getShownPlan() {
    return $("#dropdown-plan-label").html();
}

function setCurrentTime(time) {
    $("#current-time").text(time);
}

function setAutoRunShow(enabled) {
    const button = $("#auto");
    if (enabled) {
        button.removeClass("btn-secondary").addClass("btn-primary");
    } else {
        button.removeClass("btn-primary").addClass("btn-secondary");
    }
}

function showError(message) {
    alert("Error: " + message);
}

/* API Adapter Functions */
function getPlans(callback) {
    $.get("/plans", function(data) {
        callback(JSON.parse(data));
    }).fail(function(jqXHR, textStatus) {
        showError(jqXHR.responseText);
    });
}

function getExprData(plan, callback) {
    const url = "/expr_data?plan=" + plan;
    $.get(url, function(data) {
        callback(JSON.parse(data));
    }).fail(function(jqXHR, textStatus) {
        showError(jqXHR.responseText);
    });
}

/* Controllers */
var autoRun = false;
function toggleAutoRun() {
    autoRun = !autoRun;
    setAirportShow(autoRun);
}

/* Main */
$("document").ready(function(){
    loadOptions();
    const params = getParams();
    if ("plan" in params) {
        const plan = params["plan"];
        setPlanShow(plan);
        loadExprData(plan);
    }
});

function loadOptions() {
    getPlans(function(plans) {
        loadPlans(plans)
    });
}

var expr_data = null;
function loadExprData(plan) {
    getExprData(plan, function(data) {
        expr_data = data;
        setAirportCenter();
        drawSurfaceData();
    });
}

function setAirportCenter() {
    var center = expr_data["surface"]["airport_center"];
    resetMap(center["lat"], center["lng"], ZOOM_AIRPORT);
}

function drawSurfaceData() {

    // Gate
    for (let gate of expr_data["surface"]["gates"]) {
		var name = "GATE: " + gate["name"];
        drawNode(gate["lat"], gate["lng"], GATE_ICON_URL, name);
    }

    // Spot
    for (let spot of expr_data["surface"]["spots"]) {
		var name = "SPOT POSITION: " + spot["name"];
        drawNode(spot["lat"], spot["lng"], SPOT_ICON_URL, name);
    }

    // Pushback way
    for (let pushback_way of expr_data["surface"]["pushback_ways"]) {
		var name = "PUSHBACK WAY: " + pushback_way["name"];
        drawLink(parseNodes(pushback_way["nodes"]), PUSHBACK_WAY_COLOR);
    }

    // Taxiway
    for (let taxiway of expr_data["surface"]["taxiways"]) {
		var name = "PUSHBACK WAY: " + taxiway["name"];
        drawLink(parseNodes(taxiway["nodes"]), TAXIWAY_COLOR);
    }

    // Runway
    for (let runway of expr_data["surface"]["runways"]) {
		var name = "PUSHBACK WAY: " + runway["name"];
        drawLink(parseNodes(runway["nodes"]), RUNWAY_COLOR);
    }

}

function parseNodes(rawNodes) {
    var nodes = [];
    for (let node of rawNodes) {
        nodes.push({"lat": node[1], "lng": node[0]});
    }
    return nodes;
}
