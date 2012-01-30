dojo.provide("dri.Login");

dojo.require("dijit._Widget");
//dojo.require("tnt.form._BasePage");

// Provides the opening create-router page
dojo.declare("dri.Login", [dijit._Widget], {

    id: "login_widget",
    dialog: null,

    buildRendering: function() {
        this.dialog = new dijit.Dialog({id: "login_dialog", title: "Login", style: "background-color:#FFFF85;"});
        this.dom_node = dojo.byId("login_dialog");
    },

    authenticate: function(errmsg) {
        var xhrArgs = {
            url: '/login/',
            handleAs: "text",
            load: dojo.hitch(this, function(response, ioArgs) {
                this.dom_node.innerHTML = response;

                var submit_button_spec = { id: "login_submit",
                    //dojotype: "dijit.form.Button",
                    innerHTML: "Submit"
                };

                var cancel_button_spec = { id: "login_cancel",
                    hidebackground: "true", 
                    //dojotype: "dijit.form.Button",
                    innerHTML: "Cancel"
                };

                dojo.create("button", submit_button_spec, this.dom_node);
                dojo.create("button", cancel_button_spec, this.dom_node);
                dojo.create("div", {id: 'login_errmsg'}, this.dom_node);
                dojo.parser.parse(this.dom_node);

                dojo.connect(dojo.byId('login_submit'), "onclick", dojo.hitch(this, function(evt) {
                    var form = dijit.byId("login_form");
                    this.request_authentication(form.domNode);
                    dojo.stopEvent(evt);
                }));
                dojo.connect(dojo.byId('login_cancel'), "onclick", function(evt) {
                    alert("Cancel");
                    dojo.stopEvent(evt);
                });
                this.dialog.show();
            })
        };
        var deferred = dojo.xhrGet(xhrArgs);
        if (errmsg) {
            dojo.byId('login_errmsg').innerHTML = errmsg;
        }
    },

    request_authentication: function(my_form) {
        var url = "/authenticate/";
        var xhrArgs = {
            url: url,
            handleAs: "json",
            username: my_form.username.value,
            content:{username: my_form.username.value,
                password: my_form.password.value,
                csrfmiddlewaretoken: my_form.csrfmiddlewaretoken.value
            },
            load: dojo.hitch(this, function(data) {
                if (!data.success) {
                    this.login(data.message);
                } else {
                    this.dialog.hide();
                    dijit.byId("home_page").main(data.username);
                }
            })
        };
        var deferred = dojo.xhrPost(xhrArgs);
    }
});
