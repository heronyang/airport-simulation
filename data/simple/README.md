# Simple Data

## Source

Manually created at [Google Map](https://drive.google.com/open?id=1mBnfA-NOBUFodKkWZqRLZjeTrqNuW_K1&usp=sharing).

## Install

    $ pip3 install -r requirements.txt

## Generate Surface Data

    $ python3 generate.py

## Generate Scenario

    $ python3 generate_scenario.py

## (Optional) Edit Map

### Step 1: Edit on Google Map

Edit the map on [Google Map](https://drive.google.com/open?id=1mBnfA-NOBUFodKkWZqRLZjeTrqNuW_K1&usp=sharing) without making any change to the layer name.

### Step 2: Download KML file from Google Map

Click on right-top menu button of the left panel in Edit mode, then click "Export to XML" -> select "Entire map" -> check "Export to a .XML file" -> click "Download". Put the .kml file just downloaded under this folder and rename it to "airport.kml".

### Step 3: Build Map

    $ python3 generate.py

## Note

As long as you use the same format of our Google Map to export .jml file, the file will be valid for the simulation. But, please do so by copying from the original map so we can keep the map as time goes by.
