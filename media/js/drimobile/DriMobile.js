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

    switch_device: function(new_state, mac_address, csrf_token) {
        var url = "/enable_device/";
        var xhrArgs = {
            url: url,
            handleAs:"json",
            content:{mac_address: mac_address,
                     duration: 30,
                     csrfmiddlewaretoken: csrf_token
            },
            load: function(data) {
                for (variable in data) {
                    console.log(">> " + variable + ': ' + data[variable]);
                }
                console.log('mac_address in load: (' + mac_address + ')');
            },
            error: function(data) {
                console.log("ERROR:" + data);
            }
        };
        var deferred = dojo.xhrPost(xhrArgs);
        var isOn = new_state == "on";
        console.log("new_state:" + new_state);
        console.log("mac_address: " + mac_address);
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
                    
                        if (policy_name === 'upon-request') {
                            var item = new dojox.mobile.ListItem({
                                "class": "drimobileListItem user-" + 'fred'
                            }).placeAt(this.listNode,"first");
                            
                            item.containerNode.innerHTML = this.substitute(this.deviceTemplateString, {
                                mac_address: mac_address,
                                device_name: device.name || mac_address,
                                name: 'device-name',
                                avatar: 'picture-url',
                                time: device.is_allowed,
                                created_at: 'create-at',
                                id: 'main_container'
                            });

                            var switch_value = 'off';
                            if (device.is_allowed === true) {
                                switch_value = "on";
                            }

                            var userSwitch = new dojox.mobile.Switch({
                                "class": "drimobileSwitch",
                                id: mac_address + "_switch",
                                value: switch_value,
                                name: mac_address
                            }).placeAt(item.containerNode, "first");

                            // Add change event to the switch
                            dojo.connect(userSwitch, "onStateChanged", this, function(new_state) {
                                this.switch_device(new_state, mac_address, csrf_token);
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
        var item = new dojox.mobile.ListItem({
            "class": "drimobileListItem user-" + 'fred'
        }).placeAt(this.listNode,"first");
        
        item.containerNode.innerHTML = this.substitute(this.deviceTemplateString, {
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
