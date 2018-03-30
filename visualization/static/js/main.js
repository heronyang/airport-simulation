/* Map */
var map;
var nodes = [];
var links = [];

const FLIGT_ICON_URL = "/image/flight.png";

function initMap() {
	map = new google.maps.Map(document.getElementById("map"), {
		center: {lat: 0, lng: 0},
		zoom: 2
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

function drawNode(lat, lng, icon_url) {
    nodes.push(new google.maps.Marker({
        position: {lat: lat, lng: lng},
        map: map,
        icon: icon_url
    }));
}

function drawLink(nodes, color) {
    link = new google.maps.Polyline({
        path: nodes,
        strokeColor: color,
    });
    link.setMap(map);
    links.push(link);
}

function removeNodes() {
    for (var i = 0; i < nodes.length; i++) {
        nodes[i].setMap(null);
    }
    nodes = [];
}

/* UI Callbacks */
$("#submit").click(function() {
    console.log("submit");
});

$("#auto").click(function() {
    console.log("auto");
    toggleAutoRun();
});

$("#prev").click(function() {
    console.log("prev");
});

$("#next").click(function() {
    console.log("next");
});

/* UI Operations */
function loadAirports(airports) {
    var dropdown = $("#dropdown-airport");
    dropdown.empty();
    for (let airport of airports) {
        dropdown.append('<a class="dropdown-item" href="#">' +
            airport + '</a>');
    }
}

function loadPlans(plans) {
    var dropdown = $("#dropdown-plan");
    dropdown.empty();
    for (let plan of plans) {
        dropdown.append('<a class="dropdown-item" href="#">' +
            plan + '</a>');
    }
}

function setAirportShow(airport) {
    $("#dropdown-airport-label").html(airport);
}

function setPlanShow(plan) {
    $("#dropdown-plan-label").html(plan);
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

/* Controllers */
var autoRun = false;
function toggleAutoRun() {
    autoRun = !autoRun;
    setAirportShow(autoRun);
}
