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

const AIRCRAFT_SVG_ICON_PATH = "M571.771,123.555c25.121-33.626,40.157-68.538,40.23-93.48c-0.031-8.077-1.651-14.389-4.733-19.091   c-0.324-0.575-1.212-2.08-2.779-3.563c-1.558-1.546-2.958-2.372-3.261-2.539c-4.932-3.292-11.274-4.88-19.353-4.88   c-24.88,0.042-59.802,15.068-93.438,40.23c-27.188,20.345-54.378,48.997-92.017,88.673c-6.385,6.729-13.104,13.804-20.21,21.223   l-72.905-21.85l0.219-0.209c3.03-3.062,4.755-7.273,4.713-11.411c0.042-4.368-1.724-8.579-4.765-11.609l-13.166-13.187   c-3.041-3.062-7.242-4.817-11.588-4.817c-4.389,0-8.485,1.693-11.547,4.786l-19.697,19.708l-10.429-3.114   c2.247-2.853,3.49-6.416,3.448-9.927c0.042-4.431-1.672-8.558-4.754-11.62l-13.229-13.229c-3.02-3.03-7.2-4.765-11.588-4.765   c-4.368,0-8.454,1.704-11.484,4.786l-18.077,18.067l-74.128-22.205c-1.661-0.491-3.417-0.752-5.298-0.752   c-5.266,0.063-10.146,2.017-13.709,5.549l-26.061,26.071c-2.958,2.957-4.619,6.959-4.587,10.752   c-0.094,5.59,2.999,10.752,7.952,13.406l155.884,87.085c0.763,0.428,2.968,2.059,3.783,2.874l44.441,44.431   c-41.568,43.793-78.601,86.208-107.461,123.104c-2.696,3.428-5.246,6.771-7.754,10.084L33.827,381.185   c-0.585-0.073-1.244-0.126-2.08-0.126c-5.528,0.115-10.93,2.3-14.942,6.176L4.652,399.377c-2.999,2.937-4.692,6.907-4.65,10.742   c-0.094,5.852,3.448,11.264,8.767,13.636l84.838,40.293c0.731,0.366,2.633,1.714,3.25,2.33l7.043,6.991   c-2.205,6.207-3.323,11.588-3.386,16.312c-0.021,6.321,2.017,11.734,5.915,15.632l0.303,0.262l0.083,0.062   c4.002,3.877,9.185,5.852,15.601,5.852c4.619-0.073,9.948-1.17,16.176-3.364l7.147,7.137c0.554,0.585,1.881,2.445,2.226,3.187   l40.209,84.651c2.456,5.402,7.753,8.902,13.521,8.902h0.083c3.992,0,7.806-1.599,10.721-4.524l12.445-12.487   c3.688-3.887,5.862-9.247,5.945-14.9c0-0.689-0.031-1.223-0.052-1.516l-10.982-121.035c3.302-2.487,6.646-5.047,10.083-7.722   c36.949-28.903,79.374-65.968,123.083-107.473l44.473,44.515c0.721,0.689,2.403,2.895,2.895,3.814l86.918,155.602   c2.654,5.026,7.764,8.13,13.428,8.13c4.044,0,7.889-1.599,10.836-4.566l26.248-26.229c3.407-3.562,5.319-8.401,5.371-13.688   c0-1.776-0.25-3.5-0.71-5.12l-22.205-74.149l18.066-18.098c3.041-3.021,4.766-7.221,4.766-11.536c0-4.337-1.683-8.412-4.744-11.516   l-13.25-13.239c-3.03-3.041-7.221-4.775-11.536-4.775c-3.657,0-7.23,1.223-10.021,3.428l-3.104-10.387l19.718-19.718   c3.03-3.041,4.755-7.242,4.755-11.568c0-4.357-1.683-8.442-4.755-11.504l-13.188-13.188c-3.041-3.083-7.262-4.828-11.599-4.828   c-4.357,0-8.579,1.766-11.557,4.807l-0.136,0.125l-21.84-72.895c7.545-7.189,14.702-14.034,21.547-20.481   C522.932,177.766,551.479,150.681,571.771,123.555z";

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

    __drawNode(lat, lng, image, label, content) {
        const infowindow = new google.maps.InfoWindow({
            content: content
        });

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

    __getAircraftIcon(rotation, state) {
        let color;
        switch (state) {
            case "Stopped":
                color = "#e53935";
                break;
            case "Hold":
                color = "#f9a825";
                break;
            default:
                // moving
                color = "#1565c0";
                break;
        }

        return {
            path: AIRCRAFT_SVG_ICON_PATH,
            scale: 0.04,
            rotation: rotation - 45,
            strokeColor: color,
            fillColor: color,
            fillOpacity: 1,
            anchor: new google.maps.Point(306, 306)
        };
    }

    drawAircraft(lat, lng, state, name, content) {
        return this.__drawNode(lat, lng, this.__getAircraftIcon(0, state), name, content);
    }

    drawGate(lat, lng, name) {
        const image = {
            url: "/image/gate.svg",
            size: new google.maps.Size(18, 18),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(9, 9)
        };

        const gate = this.__drawNode(lat, lng, image, null, name);
        this.gates.push(gate);
    }

    drawSpot(lat, lng, name) {
        const image = {
            url: "/image/spot.svg",
            size: new google.maps.Size(18, 18),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(9, 9)
        };

        this.__drawNode(lat, lng, image, null, name);
    }

    updateAllAircraft(allAircraft, use_animation) {
        let newAircraftSet = new Map();

        for (let each of allAircraft) {
            if (this.aircraft.has(each.name)) {
                const aircraft = this.aircraft.get(each.name);
                let angle;

                if (this.__isCloseNode(
                    aircraft.getPosition().lat(),
                    aircraft.getPosition().lng(),
                    each.lat,
                    each.lng)
                ) {
                    angle = -aircraft.getIcon().rotation - 45;
                } else {
                    angle = this.__calcAngle(
                        aircraft.getPosition().lat(),
                        aircraft.getPosition().lng(),
                        each.lat,
                        each.lng
                    );
                }

                aircraft.setOptions({
                    icon: this.__getAircraftIcon(-angle, each.status)
                });


                if (use_animation) {
                    aircraft.animateTo(new google.maps.LatLng(each.lat, each.lng), {
                        easing: "linear",
                        duration: 500
                    });
                } else {
                    aircraft.setOptions({
                        position: new google.maps.LatLng(each.lat, each.lng)
                    })
                }

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

    // Calculate the bearing between two positions as a value from 0-360
    // Credit: https://stackoverflow.com/a/11415329
    __calcAngle(lat1, lng1, lat2, lng2) {
        const dLon = (lng2 - lng1);
        const y = Math.sin(dLon) * Math.cos(lat2);
        const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
        const brng = Math.atan2(y, x) * 180 / Math.PI;
        return 360 - ((brng + 360) % 360);
    }

    __isCloseNode(lat1, lng1, lat2, lng2) {
        const THRESHOLD = 0.0000001;
        return Math.abs(lat1 - lat2) < THRESHOLD && Math.abs(lng1 - lng2) < THRESHOLD;
    }
}