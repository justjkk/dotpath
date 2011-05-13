function CreateMap() {

    // Create Openlayers Map object
    map = new OpenLayers.Map({
        div: "map",
        controls:[
            new OpenLayers.Control.Navigation(),
            new OpenLayers.Control.PanZoomBar(),
            new OpenLayers.Control.Attribution(),
            new OpenLayers.Control.LayerSwitcher()
        ],
        allOverlays: true,
    });

    // Create Icons for markers
    var iconSize = new OpenLayers.Size(32,32);
    var iconOffset = new OpenLayers.Pixel(-4,-32);
    var start_icon = new OpenLayers.Icon("/static/img/start_flag.png", iconSize, iconOffset);
    var finish_icon = new OpenLayers.Icon("/static/img/checkered_flag.png", iconSize, iconOffset);

    // Add OSM Baselayer
    var osm = new OpenLayers.Layer.OSM();
    map.addLayer(osm);

    // Position map zoomed on Chennai
    map.setCenter(
        new OpenLayers.LonLat(80.2, 13.02).transform(
            new OpenLayers.Projection("EPSG:4326"),
            map.getProjectionObject()
        ),
        11 // <- default zoom level
    );

    // Create pointsLayer which contains start and stop markers
    var pointsLayer = new OpenLayers.Layer.Markers("Points");
    map.addLayer(pointsLayer);

    // Initialize markers
    start_marker = null;
    finish_marker = null;

    // Add Routing layers
    routingLayer = new OpenLayers.Layer.Vector("KML", {
        strategies: [new OpenLayers.Strategy.Fixed()],
        protocol: new OpenLayers.Protocol.HTTP({
            url: "route.kml",
            params: {"start_location" : "80.212531280499,13.043915340177",
            "finish_location": "80.273299407938,13.069834950294"},
            format: new OpenLayers.Format.KML({
                extractStyles: true,
                extractAttributes: true,
                maxDepth: 2
            })
        })
    });
    map.addLayer(routingLayer);

    // Create Click class to handle clicking on Map
    OpenLayers.Control.Click = OpenLayers.Class(
        OpenLayers.Control,
        {
            defaultHandlerOptions: {
                'single': true,
                'double': false,
                'pixelTolerance': 0,
                'stopSingle': false,
                'stopDouble': false
            },

            initialize: function(options) {
                OpenLayers.Control.prototype.initialize.apply(
                    this, arguments
                );
                this.handler = new OpenLayers.Handler.Click(
                    this,
                    {
                        'click': this.trigger
                    }
                );
            },

            // Event Handler for click
            trigger: function(e) {
                if(start_marker == null) // First click sets Start marker
                {
                    if(finish_marker != null)
                        pointsLayer.removeMarker(finish_marker);
                    start_marker = new OpenLayers.Marker(
                        map.getLonLatFromViewPortPx(e.xy),
                        start_icon.clone()
                    );
                    pointsLayer.addMarker(start_marker);
                }
                else if(finish_marker == null) // Second click sets Finish
                  // marker and draws route
                {
                    finish_marker = new OpenLayers.Marker(
                        map.getLonLatFromViewPortPx(e.xy),
                        finish_icon.clone()
                    );
                    pointsLayer.addMarker(finish_marker);
                    
                    // Convert coordinates to 4326 projection
                    var start_lonlat = start_marker.lonlat.clone().transform(
                        map.getProjectionObject(),
                        new OpenLayers.Projection("EPSG:4326")
                    );
                    var finish_lonlat = finish_marker.lonlat.clone().transform(
                        map.getProjectionObject(),
                        new OpenLayers.Projection("EPSG:4326")
                    );
                    
                    routingLayer.protocol.params.start_location = start_lonlat.lon + "," + start_lonlat.lat;
                    routingLayer.protocol.params.finish_location = finish_lonlat.lon + "," + finish_lonlat.lat;
                    routingLayer.refresh();
                }
                else // Third click resets the map
                {
                    if(start_marker != null)
                    {
                        pointsLayer.removeMarker(start_marker);
                        start_marker.destroy();
                        start_marker = null;
                    }
                    if(finish_marker != null)
                    {
                        pointsLayer.removeMarker(finish_marker);
                        finish_marker.destroy();
                        finish_marker = null;
                    }
                }
            }
        }
    );

    // Bind click event handler to map
    var click = new OpenLayers.Control.Click();
    map.addControl(click);
    click.activate()
}
