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

function loadExprData(plan) {
    getExprData(plan, function(data) {
        console.log(data);
    });
}
