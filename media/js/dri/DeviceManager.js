dojo.provide("dri.DeviceManager");

dojo.require("dijit._Widget");
dojo.require("dri._Manager");

// Provides the opening create-router page
dojo.declare("dri.DeviceManager", [dijit._Widget, dri._Manager], {

    id: "device_manager",
    dojango_waste: ['edit_pane', 'id_device_name', 'id_policy', 'id_mac_address',
                    'id_device_type', 'id_device_allowed'],

    // Parse server data, returning a tree that can be rendered in an accordion
    generate_device_tree: function(server_data) {
        var tree = {};
        var description;
        for (var mac_address in server_data) {
            if (mac_address === 'success') {
                continue;
            }
            if (mac_address === 'csrf') {
                continue;
            }
            if (server_data.hasOwnProperty(mac_address)) {
                var device = server_data[mac_address];
                description = "Unknown";
                if (device.type !== null) {
                    description = device.type.description;
                }
                if (!tree[description]) {
                    tree[description] = [];
                }
                tree[description].push({'name': device.name,
                    'suggested_name': device.suggested_name,
                    'mac_address': mac_address
                });
            }
        }
        return tree;
    },

    populate_accordion: function() {
        var xhrArgs = {
            url: '/known_devices/',
            handleAs: "json",
            load: dojo.hitch(this, function(response, ioArgs) {
                var container = dojo.byId("known_devices");
                container.innerHTML = ''; // Clear out old stuff
                tree = this.generate_device_tree(response.valueOf());

                for (description in tree) {
                    dojo.create("h3", {innerHTML: description}, container);
                    var devices = tree[description];
                    var list_holder = dojo.create("ul", {}, container);
                    for (i=0; i<devices.length; i++) {
                        var device_name = devices[i].name || devices[i].suggested_name || devices[i].mac_address;
                        var list_item = dojo.create("li", {}, list_holder);
                        var button_name = devices[i].mac_address + "_manage_button";
                        var button_spec = { id: button_name,
                                            name: devices[i].mac_address,
                                            hidebackground: "true", 
                                            //dojotype: "dijit.form.Button",
                                            innerHTML: device_name
                        };
                        var manage_button = dojo.create("button", button_spec, list_item);
                        var handle = dojo.connect(dojo.byId(button_name), "onclick", dojo.hitch(this, function(evt) {
                            this.show(evt.target.name);
                        }));
                    }
                }
                dojo.parser.parse(container);
            }),
            error: function(error) {
                var container = dojo.byId("known_devices");
                container.innerHTML = "An unexpected error occurred: " + error;
            }
        };
        var deferred = dojo.xhrGet(xhrArgs);
    },

    show: function(mac_address) {
        var xhrArgs = {
            url: '/device/' + mac_address,
            handleAs: "text",
            load: dojo.hitch(this, function(response, ioArgs) {
                this.cleanup();
                var dom_node = dojo.byId('main_pane');
                dom_node.innerHTML = response;

                var apply_button_spec = { id: "edit_device_apply",
                    name: mac_address,
                    hidebackground: "true", 
                    //dojotype: "dijit.form.Button",
                    innerHTML: "Apply"
                };
                dojo.create("button", apply_button_spec, dom_node);

                var enable_button_spec = { id: "edit_device_enable",
                    name: mac_address,
                    hidebackground: "true", 
                    //dojotype: "dijit.form.Button",
                    innerHTML: "Enable for 30 min"
                };
                dojo.create("button", enable_button_spec, dom_node);

                dojo.parser.parse(dom_node);
                this.connect_buttons();
            })
        };
        var deferred = dojo.xhrGet(xhrArgs);
    },

    connect_buttons: function() {
        dojo.connect(dojo.byId("edit_device_apply"), "onclick", dojo.hitch(this, function(evt) {
            var mac_address = evt.target.name;
            var form = dijit.byId("form_" + mac_address);
            if(form.isValid()){
                this.edit_device_finish(mac_address, form.domNode);
            } else {
                return form.validate();
            }
            return true;
        }));

        dojo.connect(dojo.byId("edit_device_enable"), "onclick", dojo.hitch(this, function(evt) {
            var mac_address = evt.target.name;
            var form= dijit.byId("form_" + mac_address);
            this.enable_device(mac_address, form.domNode);
        }));

        dojo.parser.parse(dom_node);
    },

    enable_device: function(mac_address, my_form) {
        var url = "/enable_device/";
        var xhrArgs = {
            url: url,
            handleAs:"json",
            content:{mac_address: mac_address,
                     duration: 30,
                     csrfmiddlewaretoken: my_form.csrfmiddlewaretoken.value
            },
            load: function(data) {
                var main_pane = dojo.byId("main_pane");
                console.log("SUCCESS: " + data.success);
                if (data.success === true) {
                    dojo.byId('id_device_allowed').value = "True";
                }
                dijit.byId("home_page").populate_accordions();
            }
        };
        var deferred = dojo.xhrPost(xhrArgs);
    },

    edit_device_finish: function(mac_address, my_form) {
        var url = "/device/" + mac_address;
        var xhrArgs = {
            url: url,
            form: my_form,
            handleAs: "text",
            load: function(data) {
                var main_pane = dojo.byId("main_pane");
                main_pane.innerHTML += data;
                dijit.byId("home_page").populate_accordions();
            }
        };
        var deferred = dojo.xhrPost(xhrArgs);
    }
});

