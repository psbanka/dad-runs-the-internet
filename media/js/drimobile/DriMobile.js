// Provide the UI class
dojo.provide("drimobile.DriMobile");

// Dependencies here
dojo.require("drimobile._ViewMixin");
dojo.require("dojox.mobile.ScrollableView");
dojo.require("dojo.DeferredList");
dojo.require("dojo.io.script");

// Require localization for time
dojo.require("dojo.i18n");
dojo.requireLocalization("dojo.cldr", "gregorian", "", "");

// Declare the class;  inherits from ScrollableView
dojo.declare("drimobile.DriMobile", [dojox.mobile.ScrollableView, drimobile._ViewMixin], {
	
	// Create a template string for devices:
	deviceTemplateString: '<img src="${avatar}" alt="${name}" class="drimobileAvatar" />' + 
	'<div class="drimobileTime" data-dojo-time="${created_at}">${time}</div>' +
	'<div class="drimobileContent"> ' +
		'<div class="drimobileUser">${user}</div>' + 
		'<div class="drimobileText">${text}</div>' + 
	'</div><div class="drimobileClear"></div>',
	
	// Icon for loading...
	iconLoading: "js/drimobile/resources/images/loading.gif",
	// iconLoading: "js/drimobile/resources/images/androidLoading.gif"
	
	// URL to pull devices from; simple template included
	serviceUrl: "http://twitter.com/statuses/user_timeline/${account}.json?since_id=${since_id}",

	// When the widgets have started....
	startup: function() {
		// Retain functionality of startup in dojox.mobile.ScrollableView
		this.inherited(arguments);
		
		// Get the refresh button and image
		//this.refreshButton = dijit.byId(dojo.query(".drimobileRefresh",this.domNode)[0].id);
		this.refreshButton = dijit.byId(this.getElements("drimobileRefresh", this.domNode)[0].id);
		this.iconImage = this.refreshButton.iconNode.src;
		
		// Add a click handler to the button that calls refresh
		dojo.connect(this.refreshButton, "onClick", this, "refresh");
		
		// Add CSS class for styling
		dojo.addClass(this.domNode, "drimobilePane");
		
		// Get the list widget
		this.listNode = this.getListNode();
		
		// Hide the list because it's not populated with list items yet
		this.showListNode(false);
		
		// Get localization for device times
		// Get the i18n
		this.l10n = dojo.i18n.getLocalization("dojo.cldr", "gregorian");
		
		// Every 60 seconds, update the times
		setInterval(dojo.hitch(this, function() {
			//dojo.query(".drimobileTime",this.domNode).forEach(function(timeNode) {
			dojo.forEach(this.getElements("drimobileTime",this.domNode), function(timeNode) {
				timeNode.innerHTML = this.formatTime(dojo.attr(timeNode, "data-dojo-time"));
			},this);
		}),60000);
		
	},
	
	// Contacts twitter to receive devices
	refresh: function() {
		// Updates the refresh icon
		this.refreshButton.iconNode.src = this.iconLoading;
		
		// Button has been "pressed"
		this.refreshButton.select();
		
		// For every account, add the deferred to the list
		var defs = [], accounts = drimobile.ACCOUNTS;
		for(var account in accounts) {
			// If the account is enabled...
			if(accounts[account].enabled) {
				// Get devices!
				defs.push(dojo.io.script.get({
					callbackParamName: "callback",
					preventCache: true,
					timeout: 3000,
					url: this.substitute(this.serviceUrl, { account: account, since_id: accounts[account].since || 1 })
				}));
			}
		}
		
		// Create a deferredlist to handle when all devices are returned
		// Add this.onTweetsReceived as the callback
		new dojo.DeferredList(defs).addCallback(dojo.hitch(this, this.onTweetsReceived));
	},
	
	// Fires when devices are received from the controller
	updateContent: function(rawTweetData) {
		// For every device received....
		dojo.forEach(rawTweetData, function(device) {
			// Get the user's screen name
			var screenName = device.searchUser || device.user.screen_name;
			
			// Create a new list item, inject into list
			var item = new dojox.mobile.ListItem({
				"class": "drimobileListItem user-" + screenName
			}).placeAt(this.listNode,"first");
			
			// Update the list item's content using our template for devices
			item.containerNode.innerHTML = this.substitute(this.deviceTemplateString, {
				text: this.formatTweet(device.text),
				user: screenName,
				name: device.from_user || device.user.name,
				avatar: device.profile_image_url || device.user.profile_image_url,
				time: this.formatTime(device.created_at),
				created_at: device.created_at,
				id: device.id
			});
		}, this);
		// Show the list now that we have content for it
		this.showListNode(true);
	},
	
	// Adds the proper device linkification to a string
	formatTweet: function(deviceText) {
		return deviceText.
		replace(/(https?:\/\/\S+)/gi,'<a href="$1">$1</a>').
		replace(/(^|\s)@(\w+)/g,'$1<a href="http://twitter.com/$2">@$2</a>').
		replace(/(^|\s)#(\w+)/g,'$1<a href="http://search.twitter.com/search?q=%23$2">#$2</a>');
	},
	
	// Formats the time as received by Twitter
	formatTime: function(date) {
		// Get now
		var now = new Date();
		
		// Push string date into an Date object
		var deviceDate = new Date(date);
		
		// Time measurement: seconds
		var secondsDifferent = Math.floor((now - deviceDate) / 1000);
		if(secondsDifferent < 60) {
			return secondsDifferent + " " + (this.l10n['field-second']) + (secondsDifferent > 1 ? "s" : "");
		}
		
		// Time measurement: Minutes
		var minutesDifferent = Math.floor(secondsDifferent / 60);
		if(minutesDifferent < 60) {
			return minutesDifferent + " " + this.l10n['field-minute'] + (minutesDifferent > 1 ? "s" : "");
		}
		
		// Time measurement: Hours
		var hoursDifferent = Math.floor(minutesDifferent / 60);
		if(hoursDifferent < 24) {
			return hoursDifferent + " " + this.l10n['field-hour'] + (hoursDifferent > 1 ? "s" : "");
		}
		
		// Time measurement: Days
		var daysDifferent = Math.floor(hoursDifferent / 24);
		return daysDifferent + " " + this.l10n['field-day'] + (daysDifferent > 1 ? "s" : "");
	},
	
	// Merges devices into one array, sorts them
	sortTweets: function(deflist) {
		// Create an array for our devices
		var allTweets = [];
		
		// For each def list result...
		dojo.forEach(deflist, function(def) {
			// Define which property to check
			// Tweet is just "def[1]", Mentions is def[1].results
			var devices = (def[1].results ? def[1].results : def[1]);
			
			// If we received any results in this array....
			if(devices.length) {
				// Get the username and update the since
				var username = !devices[0].user ? def[1].query.replace("%40","") : devices[0].user.screen_name;
				
				// Update the since for this user
				drimobile.ACCOUNTS[username].since = devices[0].id_str;
				
				// If this is a search, we need to add the username to the device
				if(def[1].query) {
					dojo.forEach(devices, function(device) { device.searchUser = username; });
				}
				
				// Join into one big array
				allTweets = allTweets.concat(devices);
			}
		},this);
		
		// Sort them by date deviceed
		var indexedTweets = {}, timeArr = [];
		dojo.forEach(allTweets, function(device) {
			var time = new Date(device.created_at) - 0;
			indexedTweets[time] = device;
			timeArr.push(time);
		});
		timeArr.sort();
		
		// Now that they're sorted by time, push them back into an array
		var returnArray = [];
		dojo.forEach(timeArr, function(time) {
			returnArray.push(indexedTweets[time]);
		});
		
		// Return 
		return returnArray;
	},
	
	// Event for when content is loaded from Twitter
	onTweetsReceived: function(rawTweetData) {
		// Sort devices
		deviceData = this.sortTweets(rawTweetData);
		
		// Set the refresh icon back
		this.refreshButton.iconNode.src = this.iconImage;
		this.refreshButton.select(true);
		
		// If we receive new devices...
		if(deviceData.length) {
			// Update content
			this.updateContent(deviceData);
		}
	},
	
	// Updates a device's viewability by user account enable change
	onUserChange: function(account,isOn) {
		//dojo.query("li.user-" + account,this.domNode)[(isOn ? "remove" : "add") + "Class"]("drimobileHidden");
		dojo.forEach(this.getElements("user-" + account,this.domNode), function(node){ 
			dojo[(isOn ? "remove" : "add") + "Class"](node,"drimobileHidden"); 
		});
	}
		
});
