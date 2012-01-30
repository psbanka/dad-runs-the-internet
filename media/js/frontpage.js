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

