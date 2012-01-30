dojo.provide("dri._Manager");

dojo.require("dri._Manager");

// Provides the opening create-router page
dojo.declare("dri._Manager", [], {

    // Clean up mess left behind by dojango
    cleanup: function() {
        dojo.forEach(this.dojango_waste, function(id) {
            var dijit_obj = dijit.byId(id);
            var dojo_obj = dojo.byId(id);
            if (typeof dijit_obj != 'undefined') {
                dijit_obj.destroyRecursive();
            }
            if (dojo_obj !== null) {
                dojo.destroy(dojo_obj);
            }
        });
    }

});

