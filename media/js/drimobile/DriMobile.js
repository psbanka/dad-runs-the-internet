dojo.provide("drimobile.DriMobile");

dojo.require("drimobile._ViewMixin");
dojo.require("dojox.mobile.ScrollableView");

// Declare the class;  inherits from ScrollableView
dojo.declare("drimobile.DriMobile", [dojox.mobile.ScrollableView, drimobile._ViewMixin], {
	
	// Create a template string for devices:
	deviceTemplateString: //'<img src="${avatar}" alt="${name}" class="drimobileAvatar" />' + 
	'<div class="drimobileContent"> ' +
		'<div class="drimobileUser">${device_name}</div>' + 
		'<div class="drimobileText">${mac_address}</div>' + 
	'</div><div class="drimobileClear"></div>',
	
	iconLoading: "media/js/drimobile/resources/images/loading.gif",
	// iconLoading: "js/drimobile/resources/images/androidLoading.gif"
	
	startup: function() {
		this.inherited(arguments);
		this.refreshButton = dijit.byId(this.getElements("drimobileRefresh", this.domNode)[0].id);
		this.iconImage = this.refreshButton.iconNode.src;
		dojo.connect(this.refreshButton, "onClick", this, "refresh");
		dojo.addClass(this.domNode, "drimobilePane");
		this.listNode = this.getListNode();
		
		// Hide the list because it's not populated with list items yet
		this.showListNode(false);
		
		// Every 60 seconds, update the times
		setInterval(dojo.hitch(this, function() {
			//dojo.query(".drimobileTime",this.domNode).forEach(function(timeNode) {
            /*
			dojo.forEach(this.getElements("drimobileTime",this.domNode), function(timeNode) {
				timeNode.innerHTML = "time";
			},this);
            */
		}),60000);
		
	},

	refresh: function() {
        var xhrArgs = {
            url: '/known_devices/',
            handleAs: "json",
            load: dojo.hitch(this, function(response, ioArgs) { 
                data = response.valueOf();
                var csrf_token = data['csrf'].csrf_token; 
                for (var mac_address in data) {
                    if (mac_address === 'success') {
                        continue;
                    }
                    if (mac_address === 'csrf') {
                        continue;
                    }
                    if (data.hasOwnProperty(mac_address)) {
                        var device = data[mac_address];
                        
                        var policy_name = null;
                        if (device.policy !== null) {
                            policy_name = device.policy.name;
                        }
                    
                        var switch_value = 'off';
                        if (device.is_allowed === true) {
                            switch_value = "on";
                        }
                        var userSwitch;

                        if (policy_name === 'upon-request') {
                            var list_item = dijit.byId(mac_address + '_list_item');
                            if (list_item === undefined) {
                                // Create a new switch...
                                list_item = new dojox.mobile.ListItem({
                                    "class": "drimobileListItem user-" + 'fred',
                                    "id": mac_address + "_list_item"
                                }).placeAt(this.listNode,"first");
                                
                                list_item.containerNode.innerHTML = this.substitute(this.deviceTemplateString, {
                                    mac_address: mac_address,
                                    device_name: device.name || mac_address,
                                    name: 'device-name',
                                    avatar: 'picture-url',
                                    time: device.is_allowed,
                                    created_at: 'create-at',
                                    id: 'main_container'
                                });

                                userSwitch = new dojox.mobile.Switch({
                                    "class": "drimobileSwitch",
                                    id: mac_address + "_switch",
                                    value: switch_value,
                                    name: mac_address
                                }).placeAt(list_item.containerNode, "first");
                            } else {
                                // Else, just set the value
                                userSwitch = dijit.byId(mac_address + "_switch");
                                userSwitch.set("value", switch_value);
                            }

                            // Add change event to the switch
                            dojo.connect(userSwitch, "onStateChanged", mac_address, function(new_state) {
                                console.log(new_state);
                                console.log(this);

                                var url = "/enable_device/";
                                var xhrArgs = {
                                    url: url,
                                    handleAs:"json",
                                    content:{mac_address: this,
                                             duration: 30,
                                             csrfmiddlewaretoken: csrf_token
                                    },
                                    load: function(data) {
                                        for (variable in data) {
                                            console.log(">> " + variable + ': ' + data[variable]);
                                        }
                                        console.log('mac_address in load: (' + data.success + ')');
                                    },
                                    error: function(data) {
                                        console.log("ERROR:" + data);
                                        if (new_state == 'on') {
                                            userSwitch = dijit.byId(this + "_switch");
                                            userSwitch.set("value", switch_value);
                                        }
                                    }
                                };
                                var deferred = dojo.xhrPost(xhrArgs);
                                var isOn = new_state == "on";
                                console.log("new_state:" + new_state);
                                console.log("mac_address: " + this);

                            });
                        }
                    }
                }
                this.showListNode(true);
                // Set the refresh icon back
                this.refreshButton.iconNode.src = this.iconImage;
                this.refreshButton.select(true);
            })
        };
        var deferred = dojo.xhrGet(xhrArgs);

		this.refreshButton.iconNode.src = this.iconLoading;
		
		// Button has been "pressed"
		this.refreshButton.select();
		//this.load();
	},

    load: function() {
        var list_item = new dojox.mobile.ListItem({
            "class": "drimobileListItem user-" + 'fred'
        }).placeAt(this.listNode,"first");
        
        list_item.containerNode.innerHTML = this.substitute(this.deviceTemplateString, {
            mac_address: "hello",
            device_name: 'screen-name',
            name: 'device-name',
            avatar: 'picture-url',
            time: "time",
            created_at: 'create-at',
            id: 'id'
        });
		this.showListNode(true);

        // Set the refresh icon back
        this.refreshButton.iconNode.src = this.iconImage;
        this.refreshButton.select(true);

    }
	
});
