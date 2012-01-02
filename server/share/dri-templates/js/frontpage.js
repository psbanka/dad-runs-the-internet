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

function login(errmsg) {
    var xhrArgs = {
        url: '/login/',
        handleAs: "text",
        load: function(response, ioArgs) {
            var login_dialog = dijit.byId('login_dialog');
            if (typeof login_dialog == 'undefined') {
                var login_dialog = new dijit.Dialog({id: "login_dialog", title: "Login", style: "background-color:#FFFF85;"});
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

                var handle = dojo.connect(dojo.byId('login_submit'), "onclick", function(evt) {
                    var form= dijit.byId("login_form");
                    request_authentication(form.domNode);
                    dojo.stopEvent(evt);
                });
                var handle = dojo.connect(dojo.byId('login_cancel'), "onclick", function(evt) {
                    alert("Cancel");
                    dojo.stopEvent(evt);
                });
            }
            if (errmsg) {
                dojo.byId('login_errmsg').innerHTML = errmsg;
            }

            //dojo.parser.parse(dom_node);
            //dijit.byId("login_dialog").startup();
            dijit.byId("login_dialog").show();

        }
    };
    var deferred = dojo.xhrGet(xhrArgs);
}

function request_authentication(my_form) {
    var url = "/authenticate/";
    var xhrArgs = {
        url: url,
        handleAs: "json",
        content:{username: my_form.username.value,
                 password: my_form.password.value,
                 csrfmiddlewaretoken: my_form.csrfmiddlewaretoken.value
        },
        load: function(data) {
            if (!data.success) {
                login(data.message);
            } else {
                dijit.byId("login_dialog").hide();
                known_devices(data.first_name)
            }
        }
    }
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
    if (username == "__ANONYMOUS") {
        login()
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

            var apply_button_name = device_name + "_apply";
            var apply_button_spec = { id: apply_button_name,
                                      name: device_name,
                                      hidebackground: "true", 
                                      //dojotype: "dijit.form.Button",
                                      innerHTML: "Apply"
            };

            var enable_button_name = device_name + "_enable";
            var enable_button_spec = { id: enable_button_name,
                                       name: device_name,
                                       hidebackground: "true", 
                                       //dojotype: "dijit.form.Button",
                                       innerHTML: "Enable for 30 min"
            };

            dojo.parser.parse(dom_node);

            dojo.create("button", apply_button_spec, dom_node);
            dojo.create("button", enable_button_spec, dom_node);

            var handle = dojo.connect(dojo.byId(apply_button_name), "onclick", function(evt) {
                var device_name = evt.target.name;
                var form= dijit.byId("form_" + device_name);
                if(form.isValid()){
                    edit_device_finish(device_name, form.domNode);
                } else {
                    return form.validate();
                }
                return true;
            });

            var handle = dojo.connect(dojo.byId(enable_button_name), "onclick", function(evt) {
                var device_name = evt.target.name;
                var form= dijit.byId("form_" + device_name);
                enable_device(device_name, form.domNode);
            });

            dojo.parser.parse(dom_node);
        }
    };
    var deferred = dojo.xhrGet(xhrArgs);
}

function enable_device(device_name, my_form) {
    var url = "/enable_device/";
    var xhrArgs = {
        url: url,
        handleAs:"json",
        content:{device_name: device_name,
                 duration: 30,
                 csrfmiddlewaretoken: my_form.csrfmiddlewaretoken.value
        },
        load: function(data) {
            var device_tab = dojo.byId(sanitize_name(device_name)+"_tab");
            device_tab.innerHTML += data;
            known_devices("joe blow")
        }
    }
    var deferred = dojo.xhrPost(xhrArgs);
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
            known_devices("joe blow")
        }
    }
    var deferred = dojo.xhrPost(xhrArgs);
}
