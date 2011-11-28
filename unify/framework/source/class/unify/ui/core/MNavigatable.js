/* ***********************************************************************************************

    Unify Project

    Homepage: unify-project.org
    License: MIT + Apache (V2)
    Copyright: 2011, Sebastian Fastner, Mainz, Germany, http://unify-training.com

*********************************************************************************************** */

/**
 * Mixin to support navigation on widgets
 */
qx.Mixin.define("unify.ui.core.MNavigatable", {
  properties: {
    /**
     * Executes the given function on the view.
     * The function has to be public!
     */
    execute: {
      check: "String",
      init: null,
      nullable: true
    },
    
    /**
     * Opens hyperreference (=URL) in a new window
     */
    hyperreference: {
      check: "String",
      init: null,
      nullable: true
    },
    
    /**
     * Relational navigation. This property navigates relative to the current view.
     * Allowed parameters:
     * close - Close current view if it is a modal view on top of another one
     * parent - Navigate to the parent view in hierarchy
     * same - Take the same view, change segment or parameter
     * master - ?
     */
    relation: {
      check : ["close", "parent", "same", "master"],
      init: null,
      nullable: true
    },
    
    /**
     * Opens other view
     */
    goTo: {
      init: null,
      nullable: true
    },
    
    /**
     * Shows the view
     */
    show: {
      init: null,
      nullable: true
    },
    
    /**
     * Hides the view
     */
    hide: {
      init: null,
      nullable: true
    }
  },
  
  members : {
    /**
     * Applies event listeners on widget to support navigation
     */
    _applyMNavigatable : function() {
      if (this._onTap) {
        this.addListener("tap", this._onTap, this);
      } else {
        this.addListener("tap", this._tapHelper, this);
      }
      if (this._onTouchHold) {
        this.addListener("touchhold", this._onTouchHold, this);
      }
      if (this._onTouchRelease) {
        this.addListener("touchrelease", this._onTouchRelease, this);
        this.addListener("touchleave", this._onTouchRelease, this);
      }
    },
    
    /**
     * Helper function to handle taps
     *
     * @param e {qx.event.type.Tap} Tap event
     */
    _tapHelper : function(e) {
      var viewManagerWidget = this.getLayoutParent();
      var viewManager = null;
      while (!viewManager && viewManagerWidget) {
        viewManager = viewManagerWidget.getUserData("viewManager");
        viewManagerWidget = viewManagerWidget.getLayoutParent();
      }
      
      if (qx.core.Environment.get("qx.debug")) {
        if (!viewManager) {
          this.warn("Widget " + this + " has no parent view manager!");
        }
      }
      
      var exec = this.getExecute();
      if (exec) {
        viewManager.getCurrentView()[exec](this);
      } else {
        // Detect absolute links
        var href = this.getHyperreference(); //elem.getAttribute("href");
        if (href != null && href != "" && href.charAt(0) != "#") {
          window.open(href);
        } else if (!this.__navigates) {
          // Lazily navigate (omits navigation during activity)
          this.__navigates = true;
          qx.lang.Function.delay(this.__navigationWidgetHelper, 0, this, viewManager);
        }
      }
    },

    /**
     * event handler for touchhold.
     * adds state 'pressed' to this widget
     */
    _onTouchHold : function(){
      this.addState("pressed");
    },

    /**
     * event handler for touchrelease.
     * removese state 'pressed' from this widget
     */
    _onTouchRelease : function(){
      this.removeState("pressed");
    },

    /**
     * Executes navigation process on view manager
     *
     * @param viewManager {unify.view.ViewManager} View manager navigation is done on
     */
    __navigationWidgetHelper : function(viewManager) {
      // Reset event blocking flag
      this.__navigates = false;

      // Check up-navigation request first
      //var rel = elem.getAttribute("rel");
      var rel = this.getRelation();
      if (rel == "parent" || rel == "close")
      {
        var path = viewManager.getPath();
        if(path.length == 1) {
          if(viewManager.getDisplayMode()=='default'){
            viewManager.hide();
          } else {
            unify.view.PopOverManager.getInstance().hide(viewManager.getId());
          }
        } else {
          viewManager.navigate(path.slice(0, -1));
        }
        return;
      }
      
      // Support for showing/hiding another view manager (without a specific view e.g. a pop over)
      // TODO: Are there other kinds of view managers which might be shown here (not just popups)?
      //var show = elem.getAttribute("show");
      var show = this.getShow();
      if (show != null)
      {
        unify.view.PopOverManager.getInstance().show(show);
        return;
      }

      //var hide = elem.getAttribute("hide");
      var hide = this.getHide();
      if (hide != null)
      {
        unify.view.PopOverManager.getInstance().hide(hide);
        return;
      }

      // Read attributes
      //var href = elem.getAttribute("href");
      var href = this.getHyperreference();
      //var dest = href ? href.substring(1) : elem.getAttribute("goto");
      var dest = href ? href.substring(1) : this.getGoTo();
      if (dest == null) {
        throw new Error("Empty destination found!");
      }

      // Valid Paths (leading with a "#" in href attributes):
      // localView.segment:param (in transition)
      // otherView.segment:param (globally known view => delegate to navigation)
      // .segment:param (switch segment and param, no transition)
      // .segment (switch segment, no transition)
      // :param (switch param, no transition)

      if (qx.core.Environment.get("qx.debug"))
      {
        if (rel) {
          throw new Error("Invalid 'rel' attribute: " + rel);
        }
      }
      
      var config = unify.view.Path.parseFragment(dest);
      var view = config.view;
      if (view && !viewManager.getView(view))
      {
        unify.view.Navigation.getInstance().navigate(new unify.view.Path(config));
      }
      else
      {
        // Read current path and make non-deep copy of path
        var path = viewManager.getPath();
        var clone = path.concat();
        var cloneLast = clone.length-1;
        
        // Select right modification point
        if (rel == "same") 
        {
          clone[cloneLast] = config;
        } 
        else if (config.view) 
        {
          clone.push(config);
        } 
        else 
        {
          if (config.segment) {
            clone[cloneLast].segment = config.segment;
          }

          if (config.param) {
            clone[cloneLast].param = config.param;
          }
        }

        // Finally do the navigate()
        viewManager.navigate(clone);
      }
    }
  }
});