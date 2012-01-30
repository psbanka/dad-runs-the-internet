dojo.provide("dri.TrafficMatcher");

dojo.require("dijit._Widget");
dojo.require("dijit.form.ValidationTextBox");

dojo.declare("dri.TrafficMatcher", [dijit._Widget], {

    id: null,
    index: 0,
    regex: null,
    table_node: null,
    text_field: null,
    remove_link: null,

    // Create the widget
    buildRendering: function() {
        this.dom_node = dojo.create("tr", {}, this.table_node);
        var td_n = dojo.create("td", {}, this.dom_node);
        dojo.create("label", {innerHTML: "regex"}, td_n);
        var td_nplus1 = dojo.create("td", {}, this.dom_node);
        this.text_field = new dijit.form.TextBox({
            "name": "regex_" + this.index,
            value: this.regex
        }).placeAt(td_nplus1);
        var td_nplus2 = dojo.create("td", {}, this.dom_node);
        var link_text;
        if (this.regex === null) {
            this.regex = '';
            link_text = '';
        } else {
            link_text = "remove this";
        }
        var link_name = "remove_node_" + this.index;
        this.remove_link = dojo.create('a', {
            id: link_name,
            href: '#',
            innerHTML: link_text
        }, td_nplus2);
    },

    baseClass: "addListWidget",

    // Hook up our "add a thing" button to our make_another function
    postCreate: function(){
        if (this.remove_link !== null) {
            this.connect(this.remove_link, 'onclick', dojo.hitch(this, function(evt) {
                this.remove();
            }));
        }
        var link_name = "remove_node_" + this.index;
        var remove_button = dojo.byId(link_name);
        dojo.parser.parse(dojo.byId("main_pane"));
        if (this.regex === '') {
            this.connect(this.text_field, 'onChange', this.make_another);
        }
    },

    remove: function() {
        this.dom_node.hidden = true;
        dojo.destroy(this.dom_node);
        this.text_field.destroyRecursive();
    },

    make_another: function(){
        //In this case the last child will always be a AddListWidget
        tm = new dri.TrafficMatcher({index: this.index + 1,
            table_node: this.table_node
        });
        this.remove_link.innerHTML = 'remove this';
    }

});
