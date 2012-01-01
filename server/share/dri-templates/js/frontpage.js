// We don't know what state we were in when we got called, so wipe
// out extra cruft
function cleanup(id) {
    var dijit_obj = dijit.byId(id);
    var dojo_obj = dojo.byId(id);
    if (typeof dijit_obj != 'undefined') {
        dijit_obj.destroyRecursive();
    }
    if (dojo_obj !== null) {
        dojo.destroy(dojo_obj);
    }
}

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
                        edit_device_start(evt.target.name);
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

function sanitize_name(device_name) {
    return device_name.replace(' ', '').replace('"', '').replace("'", '')
}

function edit_device_start(device_name) {
    var xhrArgs = {
        url: '/edit_device/' + device_name,
        handleAs: "text",
        load: function(response, ioArgs) {
            var tab_container = dijit.byId("topTabs");
            var tab_name = sanitize_name(device_name) + "_tab"
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

            var button_name = device_name + "_apply";
            var button_spec = { id: button_name,
                                name: device_name,
                                hidebackground: "true", 
                                //dojotype: "dijit.form.Button",
                                innerHTML: "Apply"
            };

            dojo.parser.parse(dom_node);

            dojo.create("button", button_spec, dom_node);

            var handle = dojo.connect(dojo.byId(button_name), "onclick", function(evt) {
                var device_name = evt.target.name;
                var form= dijit.byId("form_" + device_name);
                if(form.isValid()){
                    edit_device_finish(device_name, form.domNode);
                } else {
                    return form.validate();
                }
                return true;
            });

            dojo.parser.parse(dom_node);
        }
    };
    var deferred = dojo.xhrGet(xhrArgs);
}

function edit_device_finish(device_name, my_form) {
    var url = "/edit_device/" + device_name;
    var xhrArgs = {
        url: url,
        form: my_form,
        handleAs: "text",
        load: function(data) {
            var device_tab = dojo.byId(sanitize_name(device_name)+"_tab");
            device_tab.innerHTML += data;
            frontpage("joe blow")
        }
    }
    var deferred = dojo.xhrPost(xhrArgs);
}
