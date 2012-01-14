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

function login(username, errmsg) {
    var xhrArgs = {
        url: '/login/',
        handleAs: "text",
        load: function(response, ioArgs) {
            var login_dialog = dijit.byId('login_dialog');
            if (typeof login_dialog == 'undefined') {
                login_dialog = new dijit.Dialog({id: "login_dialog", title: "Login", style: "background-color:#FFFF85;"});
                var dom_node = dojo.byId("login_dialog");
                dom_node.innerHTML = response;

                var submit_button_spec = { id: "login_submit",
                                           //dojotype: "dijit.form.Button",
                                           innerHTML: "Submit"
                };

                var cancel_button_spec = { id: "login_cancel",
                                           hidebackground: "true", 
                                           //dojotype: "dijit.form.Button",
                                           innerHTML: "Cancel"
                };

                dojo.create("button", submit_button_spec, dom_node);
                dojo.create("button", cancel_button_spec, dom_node);
                dojo.create("div", {id: 'login_errmsg'}, dom_node);
                dojo.parser.parse(dom_node);

                dojo.connect(dojo.byId('login_submit'), "onclick", function(evt) {
                    var form= dijit.byId("login_form");
                    request_authentication(form.domNode);
                    dojo.stopEvent(evt);
                });
                dojo.connect(dojo.byId('login_cancel'), "onclick", function(evt) {
                    alert("Cancel");
                    dojo.stopEvent(evt);
                });
            }
            if (errmsg) {
                dojo.byId('login_errmsg').innerHTML = errmsg;
            }

            if (username === "__ANONYMOUS") {
                //dojo.parser.parse(dom_node);
                //dijit.byId("login_dialog").startup();
                dijit.byId("login_dialog").show();
            } else {
                known_devices("bypassed login screen for known-user");
            }
        }
    };
    var deferred = dojo.xhrGet(xhrArgs);
}

function request_authentication(my_form) {
    var url = "/authenticate/";
    var xhrArgs = {
        url: url,
        handleAs: "json",
        username: my_form.username.value,
        content:{username: my_form.username.value,
                 password: my_form.password.value,
                 csrfmiddlewaretoken: my_form.csrfmiddlewaretoken.value
        },
        load: function(data) {
            if (!data.success) {
                login(this.username, data.message);
            } else {
                dijit.byId("login_dialog").hide();
                known_devices(data.first_name);
            }
        }
    };
    var deferred = dojo.xhrPost(xhrArgs);
}

// Our basic home-page for the app
function known_devices(username) {
    var xhrArgs = {
        url: '/known_devices/',
        handleAs: "json",
        container: dojo.byId("known_devices"),
        load: function(response, ioArgs) {
            this.container.innerHTML = ''; // Clear out old stuff
            data = response.valueOf();
            var tree = {};
            var description;
            for (var mac_address in data) {
                if (mac_address === 'success') {
                    continue;
                }
                if (mac_address === 'csrf') {
                    continue;
                }
                if (data.hasOwnProperty(mac_address)) {
                    var device = data[mac_address];
                    description = "Unknown";
                    if (device.type !== null) {
                        description = device.type.description;
                    }
                    if (!tree[description]) {
                        tree[description] = [];
                    }
                    tree[description].push({'name': device.name, 'mac_address': mac_address});
                }
            }
                     
            for (description in tree) {
                dojo.create("h3", {innerHTML: description}, this.container);
                var devices = tree[description];
                var list_holder = dojo.create("ul", {}, this.container);
                for (i=0; i<devices.length; i++) {
                    var device_name = devices[i].name || devices[i].mac_address;
                    var list_item = dojo.create("li", {}, list_holder);
                    var button_name = devices[i].mac_address + "_manage_button";
                    var button_spec = { id: button_name,
                                        name: devices[i].mac_address,
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
    if (username == "__ANONYMOUS") {
        login();
    }
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
    return device_name.replace(' ', '').replace('"', '').replace("'", '');
}

function edit_device_start(mac_address) {
    var xhrArgs = {
        url: '/edit_device/' + mac_address,
        handleAs: "text",
        load: function(response, ioArgs) {
            // Clean up mess left behind by dojango
            cleanup('edit_pane');
            cleanup('id_device_name');
            cleanup('id_policy');
            cleanup('id_mac_address');
            cleanup('id_device_type');
            cleanup('id_device_allowed');
            var dom_node = dojo.byId('main_pane');
            dom_node.innerHTML = response;

            var apply_button_spec = { id: "edit_device_apply",
                                      name: mac_address,
                                      hidebackground: "true", 
                                      //dojotype: "dijit.form.Button",
                                      innerHTML: "Apply"
            };

            var enable_button_spec = { id: "edit_device_enable",
                                       name: mac_address,
                                       hidebackground: "true", 
                                       //dojotype: "dijit.form.Button",
                                       innerHTML: "Enable for 30 min"
            };

            dojo.parser.parse(dom_node);

            dojo.create("button", apply_button_spec, dom_node);
            dojo.create("button", enable_button_spec, dom_node);

            dojo.connect(dojo.byId("edit_device_apply"), "onclick", function(evt) {
                var mac_address = evt.target.name;
                var form = dijit.byId("form_" + mac_address);
                if(form.isValid()){
                    edit_device_finish(mac_address, form.domNode);
                } else {
                    return form.validate();
                }
                return true;
            });

            dojo.connect(dojo.byId("edit_device_enable"), "onclick", function(evt) {
                var mac_address = evt.target.name;
                var form= dijit.byId("form_" + mac_address);
                enable_device(mac_address, form.domNode);
            });

            dojo.parser.parse(dom_node);
        }
    };
    var deferred = dojo.xhrGet(xhrArgs);
}

function enable_device(mac_address, my_form) {
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
            known_devices("joe blow");
        }
    };
    var deferred = dojo.xhrPost(xhrArgs);
}

function edit_device_finish(mac_address, my_form) {
    var url = "/edit_device/" + mac_address;
    var xhrArgs = {
        url: url,
        form: my_form,
        handleAs: "text",
        load: function(data) {
            var main_pane = dojo.byId("main_pane");
            main_pane.innerHTML += data;
            known_devices("joe blow");
        }
    };
    var deferred = dojo.xhrPost(xhrArgs);
}
