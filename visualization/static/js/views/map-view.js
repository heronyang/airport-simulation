"use strict";

// NASA Ame Research Center
const DEFAULT_LAT = 37.4088, DEFAULT_LNG = -122.0644, DEFAULT_ZOOM = 17;

class MapView {
    constructor(rootElement) {
        this.map = new google.maps.Map(rootElement, {
            center: {lat: DEFAULT_LAT, lng: DEFAULT_LNG},
            zoom: DEFAULT_ZOOM,
            styles: [
                {
                    featureType: "all",
                    elementType: "labels",
                    stylers: [{visibility: "off"}]
                },
            ]
        });

    }

    init(lat = DEFAULT_LAT, lng = DEFAULT_LAT, zoom = DEFAULT_ZOOM) {
        this.map.setOptions({
            center: new google.maps.LatLng(lat, lng),
            zoom: zoom,
            styles: [
                {
                    featureType: "all",
                    elementType: "labels",
                    stylers: [{visibility: "off"}]
                },
            ]
        });
    }

    __drawLink(nodes, color) {
        const link = new google.maps.Polyline({
            path: nodes,
            strokeColor: color,
        });
        link.setMap(this.map);
    }

    drawRunway() {

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
}