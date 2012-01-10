// Provide the UI class
dojo.provide("drimobile.DriMobile");

// Dependencies here
dojo.require("drimobile._ViewMixin");
dojo.require("dojox.mobile.ScrollableView");

// Declare the class;  inherits from ScrollableView
dojo.declare("drimobile.DriMobile", [dojox.mobile.ScrollableView, drimobile._ViewMixin], {
	
	// Create a template string for devices:
	deviceTemplateString: //'<img src="${avatar}" alt="${name}" class="drimobileAvatar" />' + 
	'<div class="drimobileTime" data-dojo-time="${created_at}">${time}</div>' +
	'<div class="drimobileContent"> ' +
		'<div class="drimobileUser">${user}</div>' + 
		'<div class="drimobileText">${text}</div>' + 
	'</div><div class="drimobileClear"></div>',
	
	iconLoading: "media/js/drimobile/resources/images/loading.gif",
	// iconLoading: "js/drimobile/resources/images/androidLoading.gif"
	
	startup: function() {
		this.inherited(arguments);
		
		//this.refreshButton = dijit.byId(dojo.query(".drimobileRefresh",this.domNode)[0].id);
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
			dojo.forEach(this.getElements("drimobileTime",this.domNode), function(timeNode) {
				timeNode.innerHTML = "time";
			},this);
		}),60000);
		
	},
	
	refresh: function() {
        var xhrArgs = {
            url: '/known_devices/',
            handleAs: "json",
            load: dojo.hitch(this, function(response, ioArgs) { 
                data = response.valueOf();
                for (var mac_address in data) {
                    if (mac_address === 'success') {
                        continue;
                    }
                    if (data.hasOwnProperty(mac_address)) {
                        console.log(mac_address);
                        var device = data[mac_address];
                    
                        var item = new dojox.mobile.ListItem({
                            "class": "drimobileListItem user-" + 'fred'
                        }).placeAt(this.listNode,"first");
                        
                        item.containerNode.innerHTML = this.substitute(this.deviceTemplateString, {
                            text: mac_address,
                            user: device.name || mac_address,
                            name: 'device-name',
                            avatar: 'picture-url',
                            time: device.is_allowed,
                            created_at: 'create-at',
                            id: 'id'
                        });
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
            text: "hello",
            user: 'screen-name',
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
