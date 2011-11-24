/* ***********************************************************************************************

    Unify Project

    Homepage: unify-project.org
    License: MIT + Apache (V2)
    Copyright: 2011, Sebastian Fastner, Mainz, Germany, http://unify-training.com

*********************************************************************************************** */

/**
 * EXPERIMENTAL
 *
 * Overlay container widget
 */
qx.Class.define("unify.ui.container.Overlay", {
  extend : unify.ui.container.Composite,
  
  include : [unify.ui.core.MChildControl, qx.ui.core.MRemoteChildrenHandling],
  
  events : {
    /** Event thrown if overlay visibility is changed to hidden */
    "hidden" : "qx.event.type.Event",
    
    /** Event thrown if overlay visibility is changed to shown */
    "shown" : "qx.event.type.Event"
  },
  
  properties : {
    // overridden
    appearance : {
      refine: true,
      init: "overlay"
    },
    
    /** Paint arrow */
    arrow : {
      check: "Boolean",
      init: true,
      apply: "__applyArrow"
    }
  },
  
  /**
   * @param arrowDirection {String} Direction of arrow (left, top, right, bottom)
   * @param arrowAlignment {String} Alignment of arrow on container (top, center, bottom or left, center, right)
   */
  construct : function(arrowDirection, arrowAlignment) {
    this.base(arguments, new unify.ui.layout.OverlayLayout());
    
    this._excludeChildControl("arrow");
    this._showChildControl("container");
    
    this.__arrowDirection = arrowDirection;
    this.__arrowAlignment = arrowAlignment;
    if (arrowDirection && arrowAlignment) {
      this.setArrow(true);
    }
  },
  
  members : {
    __arrowDirection : null,
    __arrowAlignment : null,
    
    /**
     * Gets inner content container
     *
     * @return {unify.ui.core.Widget} Content widget
     */
    getChildrenContainer : function() {
      return this.getChildControl("container");
    },
    
    /**
     * Returns child control widget identified by id
     *
     * @param id {String} ID of child widget
     * @return {unify.ui.core.Widget} Content widget
     */
    _createChildControlImpl : function(id) {
      var control;
      
      if (id == "arrow") {
        control = new unify.ui.other.Arrow();
        control.setWidth(18);
        control.setHeight(38);
        control.setDirection(this.__arrowDirection);
        this._addAt(control, 0, {
          type: "arrow",
          alignment: this.__arrowAlignment
        });
      } else if (id == "container") {
        control = new unify.ui.container.Composite(new qx.ui.layout.Canvas());
        control.setAppearance(this.getAppearance() + "/" + id);
        this._add(control);
      }
      
      return control || this.base(arguments, id);
    },
    
    __applyArrow : function(show) {
      if (show) {
        this._showChildControl("arrow");
      } else {
        this._excludeChildControl("arrow");
      }
    },
    
    /**
     * Calculates a position hint to align overlay to trigger widget
     */
    __getPositionHint : function() {
      var left = 0;
      var top = 0;
      
      var arrowHeight = 38;
      
      var direction = this.__arrowDirection;
      var alignment = this.__arrowAlignment;
      
      if (direction == "right") {
        left = this.getWidth();
      } else if (direction == "bottom") {
        top = this.getHeight();
      }
      
      if (alignment == "center") {
        if (direction == "left" || direction == "right") {
          top = Math.round(this.getHeight() / 2);
        } else {
          left = Math.round(this.getWidth() / 2);
        }
      } else if (alignment == "bottom") {
        top = this.getHeight() - Math.round(arrowHeight/2);
      } else if (alignment == "right") {
        left = this.getWidth() - Math.round(arrowHeight/2);
      } else if (alignment == "top") {
        top = Math.round(arrowHeight / 2);
      } else if (alignment == "left") {
        left = Math.round(arrowHeight / 2);
      }
      
      return {
        left: left,
        top: top
      };
    },
    
    /**
     * Shows overlay
     *
     * @param left {Integer?null} If set along with top align the overlay to match this position with the arrow
     * @param top {Integer?null} If set along with top align the overlay to match this position with the arrow
     */
    show : function(left, top) {
      this.setVisibility("visible");
      
      if (left && top) {
        var posHint = this.__getPositionHint();
        
        this.getLayoutParent().add(this, {
          left: left - posHint.left,
          top: top - posHint.top
        });
      }
      
      this.fireEvent("shown");
    },
    
    /**
     * Hides overlay
     */
    hide : function() {
      this.setVisibility("hidden");
      this.fireEvent("hidden");
    }
  }
});