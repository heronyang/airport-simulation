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
            "color": "#ffcc80"
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
            "color": "#e8e5ea"
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

        this.map.addListener('zoom_changed', this.__zoomChangeHandler.bind(this));
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
            strokeOpacity: 0.8,
            strokeWeight: weight
        });
        link.setMap(this.map);
        return link;
    }

    drawRunway(nodes) {
        const link = this.__drawLink(nodes, "#ffcc80", RUNWAY_UNIT_LINK_WEIGHT / ZOOM_FACTORS[this.map.getZoom()]);
        this.runways.push(link);
    }

    drawTaxiway(nodes) {
        const link = this.__drawLink(nodes, "#4db6ac", TAXIWAY_UNIT_LINK_WEIGHT / ZOOM_FACTORS[this.map.getZoom()]);
        this.taxiways.push(link);
    }

    drawPushbackWay(nodes) {
        const link = this.__drawLink(nodes, "#90a4ae", PUSHBACKWAY_UNIT_LINK_WEIGHT / ZOOM_FACTORS[this.map.getZoom()]);
        this.pushbackways.push(link);
    }

    __drawNode(lat, lng, icon_url, label, content, is_center) {
        const infowindow = new google.maps.InfoWindow({
            content: content
        });

        let image;
        if (is_center !== undefined) {
            image = {
                url: icon_url,
                // This marker is 20 pixels wide by 32 pixels high.
                size: new google.maps.Size(36, 36),
                // The origin for this image is (0, 0).
                origin: new google.maps.Point(0, 0),
                // The anchor for this image is the base of the flagpole at (0, 32).
                anchor: new google.maps.Point(18, 18)
            };
        } else {
            image = icon_url;
        }

        const marker = new google.maps.Marker({
            position: {lat: lat, lng: lng},
            map: this.map,
            label: label,
            icon: image
        });

        marker.addListener("click", function () {
            infowindow.open(this.map, marker);
        });

        return marker;
    }

    drawAircraft() {

    }

    drawGate() {

    }

    drawSpot() {

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