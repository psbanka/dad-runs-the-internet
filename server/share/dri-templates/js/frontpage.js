// Our basic home-page for the app
function frontpage(username) {
    var xhrArgs = {
        url: '/known_devices/',
        handleAs: "json",
        container: dojo.byId("known_devices"),
        load: function(response, ioArgs) {
            this.container.innerHTML = ''; // Clear out old stuff
            for (classification in response.devices) {
                dojo.create("h3", {innerHTML: classification}, this.container);
                var device_names = response.devices[classification];
                var list_holder = dojo.create("ul", {}, this.container);
                for (i=0; i<device_names.length; i++) {
                    var device_name = device_names[i];
                    var list_item = dojo.create("li", {}, list_holder);
                    var button_name = device_name + "_manage_button";
                    var button_spec = { id: button_name,
                                        name: device_name,
                                        hidebackground: "true", 
                                        //dojotype: "dijit.form.Button",
                                        innerHTML: device_name
                    };
                    var manage_button = dojo.create("button", button_spec, list_item);
                    var handle = dojo.connect(dojo.byId(button_name), "onclick", function(evt) {
                        edit_device(evt.target.name);
                    });
                }
            }
            dojo.parser.parse(this.container);
        },
        error: function(error) {
            this.container.innerHTML = "An unexpected error occurred: " + error;
        }
    };
    var deferred = dojo.xhrGet(xhrArgs);
    /*
    // There is some kind of bug with Dojo or I don't understand what's going on.
    // When I flag the dojoType, the dojo.connect doesn't work.
    var biggy_spec = {id: "biggy",
                      //dojoType: "dijit.form.Button",
                      innerHTML: "BIG BUTTON",
    }
    dojo.create("button", biggy_spec, "known_devices");
    dojo.connect(dojo.byId("biggy"), "onclick", function(evt) {
        alert('clicked' + dojo.version);
    });
    dojo.parser.parse(dojo.byId('known_devices'));
    */
}

function edit_device(device_name) {
    var xhrArgs = {
        url: '/edit_device/' + device_name,
        handleAs: "text",
        load: function(response, ioArgs) {
            var tab_container = dijit.byId("topTabs");
            var tab_name = device_name+"_tab"
            var tab_spec = {id: tab_name,
                            closable: "true",
                            title: device_name,
                            style: "padding:10px;"
            }
            var device_tab = new dijit.layout.ContentPane(tab_spec);
            tab_container.addChild(device_tab);
            tab_container.selectChild(device_tab);
            var dom_node = dojo.byId(tab_name);
            dom_node.innerHTML = response;

            dojo.parser.parse(dom_node);
        }
    };
    var deferred = dojo.xhrGet(xhrArgs);
}
