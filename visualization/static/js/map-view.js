"use strict";

// NASA Ame Research Center
const DEFAULT_LAT = 37.4088, DEFAULT_LNG = -122.0644, DEFAULT_ZOOM = 16;
const MAP_STYLE = [
    {
        "elementType": "labels",
        "stylers": [{
            "visibility": "off"
        }]
    }, {
        "featureType": "administrative.neighborhood",
        "stylers": [{
            "visibility": "off"
        }]
    }, {
        "featureType": "landscape.man_made",
        "elementType": "geometry.stroke",
        "stylers": [{
            "color": "#dcded4"
        }, {
            "weight": 1
        }]
    }, {

        "featureType": "road",
        "stylers": [{
            "visibility": "off"
        }]
    }, {
        "featureType": "transit.station.airport",
        "elementType": "geometry.fill",
        "stylers": [{
            "lightness": 10
        }]
    }, {
        "featureType": "transit.station.airport",
        "elementType": "geometry.stroke",
        "stylers": [{
            "color": "#efeff0"
        }, {
            "lightness": -15
        }]
    }, {
        "featureType": "water",
        "stylers": [{
            "saturation": 25
        }]
    }, {
        "featureType": "water",
        "elementType": "geometry.fill",
        "stylers": [{
            "color": "#dfeaef"
        }]
    }
];

const ZOOM_FACTORS = {
    20: 1128.497220,
    19: 2256.994440,
    18: 4513.988880,
    17: 9027.977761,
    16: 18055.955520,
    15: 36111.911040,
    14: 72223.822090,
    13: 144447.644200,
    12: 288895.288400,
    11: 577790.576700,
    10: 1155581.153000,
    9: 2311162.307000,
    8: 4622324.614000,
    7: 9244649.227000,
    6: 18489298.450000,
    5: 36978596.910000,
    4: 73957193.820000,
    3: 147914387.600000,
    2: 295828775.300000,
    1: 591657550.500000
};

const RUNWAY_UNIT_LINK_WEIGHT = 12 * ZOOM_FACTORS[DEFAULT_ZOOM],
    TAXIWAY_UNIT_LINK_WEIGHT = 12 * ZOOM_FACTORS[DEFAULT_ZOOM],
    PUSHBACKWAY_UNIT_LINK_WEIGHT = 8 * ZOOM_FACTORS[DEFAULT_ZOOM];

class MapView {
    constructor(rootElement) {
        this.map = new google.maps.Map(rootElement, {
            center: {lat: DEFAULT_LAT, lng: DEFAULT_LNG},
            zoom: DEFAULT_ZOOM,
            mapTypeControlOptions: {
                style: google.maps.MapTypeControlStyle.DROPDOWN_MENU,
                position: google.maps.ControlPosition.TOP_RIGHT
            },
            zoomControl: false,
            scaleControl: false,
            streetViewControl: false,
            rotateControl: false,
            fullscreenControl: false,
            styles: MAP_STYLE
        });

        this.runways = [];
        this.pushbackways = [];
        this.taxiways = [];
        this.aircraft = new Map();
        this.gates = [];
        this.spots = [];

        this.map.addListener('zoom_changed', this.__zoomChangeHandler.bind(this));

        initMarkerAnimate();
    }

    init(lat = DEFAULT_LAT, lng = DEFAULT_LAT, zoom = DEFAULT_ZOOM) {
        this.map.setOptions({
            center: new google.maps.LatLng(lat, lng),
            zoom: zoom
        });
    }

    __drawLink(nodes, color, weight) {
        const link = new google.maps.Polyline({
            path: nodes,
            strokeColor: color,
            strokeOpacity: 0.9,
            strokeWeight: weight
        });
        link.setMap(this.map);
        return link;
    }

    drawRunway(nodes) {
        const link = this.__drawLink(nodes, "#9fa8da", RUNWAY_UNIT_LINK_WEIGHT / ZOOM_FACTORS[this.map.getZoom()]);
        this.runways.push(link);
    }

    drawTaxiway(nodes) {
        const link = this.__drawLink(nodes, "#6ae4a4", TAXIWAY_UNIT_LINK_WEIGHT / ZOOM_FACTORS[this.map.getZoom()]);
        this.taxiways.push(link);
    }

    drawPushbackWay(nodes) {
        const link = this.__drawLink(nodes, "#90a4ae", PUSHBACKWAY_UNIT_LINK_WEIGHT / ZOOM_FACTORS[this.map.getZoom()]);
        this.pushbackways.push(link);
    }

    __drawNode(lat, lng, icon_url, label, content) {
        const infowindow = new google.maps.InfoWindow({
            content: content
        });

        let image = {
            url: icon_url,
            // This marker is 20 pixels wide by 32 pixels high.
            size: new google.maps.Size(24, 24),
            // The origin for this image is (0, 0).
            origin: new google.maps.Point(0, 0),
            // The anchor for this image is the base of the flagpole at (0, 32).
            anchor: new google.maps.Point(12, 12)
        };

        const marker = new google.maps.Marker({
            position: {lat: lat, lng: lng},
            map: this.map,
            label: label,
            icon: image,
            zIndex: 999
        });

        marker.addListener("click", function () {
            infowindow.open(this.map, marker);
        });

        return marker;
    }

    drawAircraft(lat, lng, state, name, content) {
        let iconUrl;
        switch (state) {
            case "stop":
                iconUrl = "/image/aircraft.png";
                break;
            case "delayed":
                iconUrl = "/image/aircraft.png";
                break;
            default:
                // moving
                iconUrl = "/image/aircraft.png";
                break;
        }

        return this.__drawNode(lat, lng, iconUrl, name, content);
    }

    drawGate(lat, lng, name) {
        const iconUrl = "/image/gate.svg";
        const gate = this.__drawNode(lat, lng, iconUrl, null, name);
        this.gates.push(gate);
    }

    drawSpot(lat, lng, name) {
        const iconUrl = "/image/spot.png";
        this.__drawNode(lat, lng, iconUrl, null, name);
    }

    updateAllAircraft(allAircraft) {
        let newAircraftSet = new Map();

        for (let each of allAircraft) {
            if (this.aircraft.has(each.name)) {
                const aircraft = this.aircraft.get(each.name);
                aircraft.animateTo(new google.maps.LatLng(each.lat, each.lng), {
                    easing: "linear",
                    duration: 500
                });
                newAircraftSet.set(each.name, aircraft);
                this.aircraft.delete(each.name);
            } else {
                const aircraft = this.drawAircraft(each.lat, each.lng, each.state, each.name, "");
                newAircraftSet.set(each.name, aircraft);
            }
        }

        // Clean previous state
        this.aircraft.forEach(v => {
            v.setMap(null);
        });

        this.aircraft = newAircraftSet;
    }

    __zoomChangeHandler() {
        for (let runway of this.runways) {
            runway.setOptions({
                strokeWeight: RUNWAY_UNIT_LINK_WEIGHT / ZOOM_FACTORS[this.map.getZoom()]
            });
        }
        for (let taxiway of this.taxiways) {
            taxiway.setOptions({
                strokeWeight: TAXIWAY_UNIT_LINK_WEIGHT / ZOOM_FACTORS[this.map.getZoom()]
            });
        }
        for (let pushbackway of this.pushbackways) {
            pushbackway.setOptions({
                strokeWeight: PUSHBACKWAY_UNIT_LINK_WEIGHT / ZOOM_FACTORS[this.map.getZoom()]
            });
        }
    }
}