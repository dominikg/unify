/* ***********************************************************************************************

    Unify Project

    Homepage: unify-project.org
    License: MIT + Apache (V2)
    Copyright: 2010, Sebastian Fastner, Mainz, Germany, http://unify-training.com

*********************************************************************************************** */

/**
 * EXPERIMENTAL
 */
qx.Class.define("unify.ui.basic.Atom", {
  extend: unify.ui.core.Widget,
  include : [unify.ui.core.MChildControl],
  
  /**
   * @param label {String} Label on atom
   * @param image {String} Image url
   */
  construct : function(label, image) {
    this.base(arguments);
    
    this._forwardStates = {
      "hover" : true,
      "pressed" : true,
      "checked" : true
    };
    
    this._setLayout(new unify.ui.layout.special.AtomLayout());
    if (label) {
      this.setText(label);
    }
    if (image) {
      this.setImage(image);
    }
  },
  
  properties : {
    /** Position of image */
    direction : {
      check : "String",
      init : "top"
    },
    
    // overridden
    appearance :
    {
      refine: true,
      init: "atom"
    },
    
    text : {
      init: null,
      apply: "_applyText"
    },
    
    image : {
      init: null,
      apply: "_applyImage"
    }
  },
  
  members: {
    __imageWidget : null,
    __labelWidget : null,
    
    _createElement : function() {
      return document.createElement("div");
    },
    
    /**
     * Returns child control widget identified by id
     *
     * @param id {String} ID of child widget
     * @return {unify.ui.core.Widget} Content widget
     */
    _createChildControlImpl : function(id) {
      var control;

      if (id == "label") {
        control = new unify.ui.basic.Label();
        this._add(control, {type: "label"});
      } else if (id == "image") {
        control = new unify.ui.basic.Image();
        this._add(control, {type: "image"});
      }

      return control || this.base(arguments, id);
    },
    
    /**
     * Set source of image
     *
     * @param value {String} URL of image
     */
    _applyImage : function(value) {
      var image = this._showChildControl("image");
      image.setSource(value);
    },
    
    /**
     * Set text on label
     *
     * @param value {String} Label text
     */
    _applyText : function(value) {
      var label = this._showChildControl("label");
      label.setValue(value);
    }
  }
});
