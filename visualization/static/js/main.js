/* Map */
var map;

const FLIGT_ICON_URL = "/image/flight.png";
const FLIGT_MOVING_ICON_URL = "/image/flight-moving.png";
const FLIGT_HOLD_ICON_URL = "/image/flight-hold.png";
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

    return marker;

}

function drawLink(nodes, color) {
    link = new google.maps.Polyline({
        path: nodes,
        strokeColor: color,
    });
    link.setMap(map);
}

/* UI Callbacks */
$("#auto").click(function(e) {
    console.log("auto");
    e.preventDefault();
    toggleAutoRun();
});

$("#prev").click(function(e) {
    e.preventDefault();
    prevState();
});

$("#next").click(function(e) {
    e.preventDefault();
    nextState();
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
var autoRunWorker = null;
function toggleAutoRun() {

    if (autoRunWorker) {
        clearInterval(autoRunWorker);
        setAutoRunShow(false);
        autoRunWorker = null;
    } else {
		autoRunWorker = window.setInterval(function() {
            nextState();
		}, 500);
        setAutoRunShow(true);
    }

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
        updateState();
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

/* State */
var state_index = 0;
function nextState() {
    state_index = (state_index + 1) % expr_data["state"].length;
    updateState();
}

function prevState() {
    state_index -= 1;
    if (state_index < 0) {
        state_index += expr_data["state"].length;
    }
    updateState();
}

var aircrafts = [];
function updateState() {

    // Clean previous state
	for (var i = 0; i < aircrafts.length; i++) {
		aircrafts[i].setMap(null);
	}
	aircrafts = [];

    // Current time
    const state = expr_data["state"][state_index];
    setCurrentTime(state["time"]);

    // Aircrafts
    for (let aircraft of expr_data["state"][state_index]["aircrafts"]) {
        aircrafts.push(drawNode(
            aircraft["location"]["lat"], aircraft["location"]["lng"],
            getAircraftIconUrl(aircraft["state"]),
            parseAircraftContent(aircraft)
        ));
    }

}

function parseAircraftContent(aircraft) {
    var html = aircraft["callsign"] + "</br>";
    if (aircraft["itinerary"] == null) {
        return html + "No itinerary";
    }
    html += "<table>";
    for (let target of aircraft["itinerary"]) {
        var latlng = target["node_location"]["lat"] + "," +
            target["node_location"]["lng"];
        html += "<tr>" + 
            "<td>" + target["node_name"] + "</td>" +
            "<td>" + latlng + "</td>" +
            "<td>" + target["eat"] + "</td>" +
            "<td>" + target["edt"] + "</td>" +
            "</tr>";
    }
    html += "</table>";
    return html;
}

function getAircraftIconUrl(aircraft_state) {
    if (aircraft_state === "moving") {
        return FLIGT_MOVING_ICON_URL;
    }
    if (aircraft_state === "hold") {
        return FLIGT_HOLD_ICON_URL;
    }
    return FLIGT_ICON_URL;
}
