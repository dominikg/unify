/* ***********************************************************************************************

    Unify Project

    Homepage: unify-project.org
    License: MIT + Apache (V2)
    Copyright: 2010, Sebastian Fastner, Mainz, Germany, http://unify-training.com

*********************************************************************************************** */

/**
 * EXPERIMENTAL
 *
 * Generic composite container widget
 */
qx.Class.define("unify.ui.container.Composite", {
  extend : unify.ui.core.Widget,
  
  include : [
    qx.ui.core.MChildrenHandling,
    qx.ui.core.MLayoutHandling
  ],
  
  /**
   * @param layout {qx.ui.layout.Abstract?null} Layout of composite
   */
  construct : function(layout) {
    this.base(arguments);
    
    if (layout) {
      this._setLayout(layout);
    }
  },
  
  properties : {
    // overridden
    appearance :
    {
      refine: true,
      init: "composite"
    }
  },
  
  members : {

  },
  
  defer : function(statics, members) {
    qx.ui.core.MLayoutHandling.remap(members);
    qx.ui.core.MChildrenHandling.remap(members);
  }
});
