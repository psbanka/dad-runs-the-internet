dojo.provide("dri.HomePage");

dojo.require("dijit._Widget");
dojo.require("dri.Login");
dojo.require("dri.DeviceManager");
dojo.require("dri.PolicyManager");

// Provides the opening create-router page
dojo.declare("dri.HomePage", [dijit._Widget], {

    id: "home_page",
    username: null,
    login_dialog: null,
    device_manager: null,
    policy_manager: null,

    // Create the widget for the first time: only executed once
    buildRendering: function() {
        this.login_dialog = new dri.Login();
    },

    check_login: function() {
        console.log("USERNAME: " + this.username);
        if (this.username == "__ANONYMOUS") {
            console.log("GETTING THE USER TO LOG ON!!");
            this.login_dialog.authenticate();
        } else {
            this.main(this.username);
        }
    },

    main: function(username) {
        this.username = username;
        this.device_manager = new dri.DeviceManager();
        this.policy_manager = new dri.PolicyManager();
        this.populate_accordions();
    },

    populate_accordions: function() {
        this.device_manager.populate_accordion();
        this.policy_manager.populate_accordion();
    }

});

