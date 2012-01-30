dojo.provide("dri.PolicyManager");

dojo.require("dijit._Widget");
dojo.require("dri._Manager");
dojo.require("dri.TrafficMatcher");
dojo.require("dijit.form.ValidationTextBox");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.form.Button");
dojo.require("dijit.TitlePane");
dojo.require("dijit.form.Form");

// Provides the opening create-router page
dojo.declare("dri.PolicyManager", [dijit._Widget, dri._Manager], {

    id: "policy_manager",
    dojango_waste: ['edit_pane', 'edit_form', 'csrf_token', 'apply_button'],
    traffic_policy: null,

    populate_accordion: function() {
        var xhrArgs = {
            url: '/policies/',
            handleAs: "json",
            load: dojo.hitch(this, function(response, ioArgs) {
                var container = dojo.byId("policies");
                container.innerHTML = ''; // Clear out old stuff

                var message = response.valueOf()['message'];
                if (response.valueOf()['success'] === false) {
                    dojo.byId("policies").innerHTML = "An unexpected error occurred: " + message;
                    return;
                }

                for (section_heading in message) {
                    dojo.create("h3", {innerHTML: section_heading}, container);
                    var traffic_policies = message[section_heading];
                    var list_holder = dojo.create("ul", {}, container);

                    for (traffic_policy_name in traffic_policies) {
                        var list_item = dojo.create("li", {}, list_holder);
                        var button_name = traffic_policy_name + "_manage_button";
                        var button_spec = { id: button_name,
                            name: traffic_policy_name,
                            hidebackground: "true", 
                            //dojotype: "dijit.form.Button",
                            innerHTML: traffic_policy_name
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
                var container = dojo.byId("policies");
                container.innerHTML = "An unexpected error occurred: " + error;
            }
        };
        var deferred = dojo.xhrGet(xhrArgs);
    },

    show: function(traffic_policy_name) {
        var xhrArgs = {
            url: '/traffic_policy/' + traffic_policy_name,
            handleAs: "json",
            load: dojo.hitch(this, function(response, ioArgs) {
                var dom_node = dojo.byId('main_pane');
                dom_node.innerHTML = '';
                var tp_data = response.valueOf("message");
                
                var edit_pane = new dijit.TitlePane({
                    region: "center",
                    title: this.traffic_policy_name,
                    id: "edit_pane"
                }).placeAt(dom_node);
                var pane_node = edit_pane.containerNode;

                var form = new dijit.form.Form({
                    //encType: 'multipart/form-data',
                    action: '',
                    id: "edit_form",
                    method: ''
                }, dojo.doc.createElement('div')).placeAt(pane_node);
                var form_node = form.containerNode;

                var table_node = dojo.create("table", {style: "display:inline"}, form_node);

                var tr_1 = dojo.create("tr", {}, table_node);
                var td_1_1 = dojo.create("td", {}, tr_1);
                var csrf_token = new dijit.form.TextBox({"type": 'hidden',
                    name: 'csrfmiddlewaretoken',
                    id: "csrf_token",
                    value: tp_data.csrf_token
                }).placeAt(td_1_1);
                var td_1_2 = dojo.create("td", {}, tr_1);
                var td_1_3 = dojo.create("td", {}, tr_1);

                var tr_2 = dojo.create("tr", {}, table_node);
                var td_2_1 = dojo.create("td", {}, tr_2);
                dojo.create("label", {innerHTML: "Description", 'for': "description"}, td_2_1);
                var td_2_2 = dojo.create("td", {}, tr_2);

                var textbox = new dijit.form.ValidationTextBox({
                    name: 'description',
                    type: 'text',
                    label: "Description",
                    value: tp_data.description
                }, dojo.doc.createElement('input')).placeAt(td_2_2);
                var td_2_3 = dojo.create("td", {}, tr_2);
                dojo.create("hr", {"class": "spacer"}, form_node);

                // Populate TrafficMatcher elements
                for(i=0; i<tp_data.traffic_matchers.length; i++) {
                    regex = tp_data.traffic_matchers[i];
                    tm = new dri.TrafficMatcher({index: i,
                        regex: regex,
                        table_node: table_node
                    });
                }
                // With an empty one at the bottom.
                tm = new dri.TrafficMatcher({index: tp_data.traffic_matchers.length,
                    table_node: table_node
                });

                var apply_button_spec = { id: "apply_button",
                    name: this.traffic_policy_name,
                    hidebackground: "true", 
                    dojotype: "dijit.form.Button",
                    innerHTML: "Apply"
                };
                dojo.create("button", apply_button_spec, form_node);

                dojo.parser.parse(dom_node);
                this.connect_buttons();
            })
        };
        this.cleanup();
        this.traffic_policy_name = traffic_policy_name;
        var deferred = dojo.xhrGet(xhrArgs);
    },

    connect_buttons: function() {
        dojo.connect(dojo.byId("apply_button"), "onclick", dojo.hitch(this, function(evt) {
            var form = dijit.byId("edit_form");
            if(form.validate()){
                dojo.stopEvent(evt);
                this.edit_finish(form.domNode);
            } else {
                alert('Form contains invalid data.  Please correct first');
                return false;
            }
            return true;
        }));
    },

    edit_finish: function(my_form) {
        var url = "/traffic_policy/" + this.traffic_policy_name;
        var xhrArgs = {
            url: url,
            form: my_form,
            handleAs: "json",
            load: function(response) {
                var message = response.valueOf()['message'];
                var main_pane = dojo.byId("main_pane");
                if (response.valueOf()['success'] === false) {
                    main_pane.innerHTML = "An unexpected error occurred: " + message;
                    return;
                }
                main_pane.innerHTML += "<h2>"+message+"</h2>";
                dijit.byId("home_page").populate_accordions();
            }
        };
        var deferred = dojo.xhrPost(xhrArgs);
    }
});


