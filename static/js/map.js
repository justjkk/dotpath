function CreateMap(routing_url) {

    // Create Openlayers Map object
    var map = new OpenLayers.Map({
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
    var pointsLayer = new OpenLayers.Layer.Markers("Flags");
    map.addLayer(pointsLayer);

    // Initialize markers
    var start_marker = null;
    var finish_marker = null;

    // Add Routing layers
    var routingLayer = new OpenLayers.Layer.Vector("KML", {
        strategies: [new OpenLayers.Strategy.Fixed()],
        styleMap: new OpenLayers.StyleMap({
            'default':{
                strokeColor: "#000000",
                strokeOpacity: 0.3,
                strokeWidth: 6,
                fillOpacity: 0.5,
                fillColor: "#aa7700",
                pointRadius: 4,
                pointerEvents: "visiblePainted",
            },
            'select':{
                strokeOpacity: 0.5,
                strokeWidth: 8,
                strokeColor: "#FF0000",
                fillColor: "#000000",
                fillOpacity: 0.7,
                pointRadius: 6,
                pointerEvents: "visiblePainted",
                label : "${label}",
                fontColor: "#000000",
                fontSize: "14pt",
                fontFamily: "Ubuntu, Arial, Tahoma, Sans-serif",
                fontWeight: "bold",
                labelAlign: "cm",
                labelXOffset: 0,
                labelYOffset: 0
            }
        }),
        protocol: new OpenLayers.Protocol.HTTP({
            url: routing_url,
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
    // Create a select feature control and add it to the map.
    var select = new OpenLayers.Control.SelectFeature(routingLayer, {hover: true});
    map.addControl(select);
    select.activate();

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
