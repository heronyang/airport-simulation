/* Map */
let mapView;

const FLIGT_ICON_URL = "/image/aircraft.png";
const FLIGT_MOVING_ICON_URL = "/image/aircraft.png";
const FLIGT_HOLD_ICON_URL = "/image/aircraft.png";
const GATE_ICON_URL = "/image/gate.svg";
const SPOT_ICON_URL = "/image/spot.png";

const QUICK_NEXT_PREV_TIMES = 120;

function initMap() {
    mapView = new MapView(document.getElementById("map"));
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

/* UI Callbacks */
$("#auto").click(function (e) {
    console.log("auto");
    e.preventDefault();
    toggleAutoRun();
});

$("#prev").click(function (e) {
    e.preventDefault();
    prevState();
});

$("#next").click(function (e) {
    e.preventDefault();
    nextState();
});

$("#prev-prev").click(function (e) {
    e.preventDefault();
    for (var i = 0; i < QUICK_NEXT_PREV_TIMES; i++) {
        prevState();
    }
});

$("#next-next").click(function (e) {
    e.preventDefault();
    for (var i = 0; i < QUICK_NEXT_PREV_TIMES; i++) {
        nextState();
    }
});

/* UI Operations */
function loadPlans(plans) {
    var dropdown = $("#dropdown-plan");
    dropdown.empty();
    for (let plan of plans) {
        dropdown.append('<a class="dropdown-item option-plan" href="#">' +
            plan + '</a>');
    }
    $(".option-plan").click(function (e) {
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
    $.get("/plans", function (data) {
        callback(JSON.parse(data));
    }).fail(function (jqXHR, textStatus) {
        showError(jqXHR.responseText);
    });
}

function getExprData(plan, callback) {
    const url = "/expr_data?plan=" + plan;
    $.get(url, function (data) {
        callback(JSON.parse(data));
    }).fail(function (jqXHR, textStatus) {
        showError(jqXHR.responseText);
    });
}

/* Controllers */
var autoRunWorker = null;
var pauseTime = 500;

function toggleAutoRun() {

    if (autoRunWorker) {
        clearInterval(autoRunWorker);
        setAutoRunShow(false);
        autoRunWorker = null;
    } else {
        autoRunWorker = window.setInterval(function () {
            nextState();
        }, pauseTime);
        setAutoRunShow(true);
    }

}

/* Main */
$("document").ready(function () {
    loadOptions();
    const params = getParams();
    if ("plan" in params) {
        const plan = params["plan"];
        setPlanShow(plan);
        loadExprData(plan);
    }
});

function loadOptions() {
    getPlans(function (plans) {
        loadPlans(plans)
    });
}

var expr_data = null;

function loadExprData(plan) {
    getExprData(plan, function (data) {
        expr_data = data;
        setAirportCenter();
        drawSurfaceData();
        updateState();
    });
}

function setAirportCenter() {
    var center = expr_data["surface"]["airport_center"];
    mapView.init(center["lat"], center["lng"]);
}

function drawSurfaceData() {

    // Gate
    for (let gate of expr_data["surface"]["gates"]) {
        const name = "GATE: " + gate["name"];
        mapView.__drawNode(gate["lat"], gate["lng"], GATE_ICON_URL, "", name, true);
    }

    // Spot
    for (let spot of expr_data["surface"]["spots"]) {
        const name = "SPOT POSITION: " + spot["name"];
        mapView.__drawNode(spot["lat"], spot["lng"], SPOT_ICON_URL, "", name, true);
    }

    // Runway
    for (let runway of expr_data["surface"]["runways"]) {
        mapView.drawRunway(parseNodes(runway["nodes"]));
    }

    // Pushback way
    for (let pushback_way of expr_data["surface"]["pushback_ways"]) {
        mapView.drawPushbackWay(parseNodes(pushback_way["nodes"]));
    }

    // Taxiway
    for (let taxiway of expr_data["surface"]["taxiways"]) {
        mapView.drawTaxiway(parseNodes(taxiway["nodes"]));
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
        aircrafts.push(mapView.__drawNode(
            aircraft["location"]["lat"], aircraft["location"]["lng"],
            getAircraftIconUrl(aircraft),
            aircraft["callsign"],
            parseAircraftContent(aircraft),
            true
        ));
    }

}

function parseAircraftContent(aircraft) {
    var html = aircraft["callsign"] + "</br>";
    if (aircraft["itinerary"] == null) {
        return html + "No itinerary";
    }
    html += "<table><tr><th>Target</th><th>LatLng</th><th>UC</th><th>SC</th></tr>";
    var index = aircraft["itinerary_index"];
    var uc_delay_index = aircraft["uncertainty_delayed_index"];
    var sc_delay_index = aircraft["scheduler_delayed_index"];
    var i = 0;
    for (let target of aircraft["itinerary"]) {
        var latlng = target["node_location"]["lat"] + "," +
            target["node_location"]["lng"];
        html += "<tr class=\"" + getTargetClassName(i, index) + "\">";
        html += "<td>" + target["node_name"] + "</td><td>" + latlng + "</td>";
        if ($.inArray(i, uc_delay_index) >= 0) {
            html += "<td>V</td>";
        } else {
            html += "<td>&nbsp;</td>";
        }
        if ($.inArray(i, sc_delay_index) >= 0) {
            html += "<td>V</td>";
        } else {
            html += "<td>&nbsp;</td>";
        }
        html += "</tr>";
        i += 1;
    }
    html += "</table>";
    return html;
}

function getTargetClassName(current_index, index) {
    if (current_index < index) {
        return "past-target";
    } else if (current_index == index) {
        return "current-target";
    }
    return "future-target";
}

function getAircraftIconUrl(aircraft) {

    if (aircraft["state"] == "stop") {
        return FLIGT_ICON_URL;
    }

    if (aircraft["is_delayed"]) {
        return FLIGT_HOLD_ICON_URL;
    }

    return FLIGT_MOVING_ICON_URL;

}
