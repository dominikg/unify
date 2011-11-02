/* 
==================================================================================================
  Jasy - JavaScript Tooling Framework
  Copyright 2010-2011 Sebastian Werner
==================================================================================================
*/

/**
 * This class is the client-side representation for the permutation features of 
 * Jasy and supports features like auto-selecting builds based on specific feature sets.
 *
 * @require {qx.core.Environment}
 */
(function(global, undef)
{
	Module("qxpatchjs.Env",
	{
		/**
		 * Configure environment data dynamically
		 *
		 * @param name {String} Name of the field to configure
		 * @param value {var} Value to set
		 */
		define : function(name, value) {
			jasy.Env.define(name, value);
		},
		
		
		/**
		 * Whether the given field was set to the given value. Boolean 
		 * fields could also be checked without a given value as the value
		 * defaults to <code>true</code>.
		 *
		 * @param name {String} Name of the field to query
		 * @param value {var?true} Value to compare to (defaults to true)
		 * @return {Boolean} Whether the field is set to the given value
		 */
		isSet : function(name, value) 
		{
			return jasy.Env.isSet(name, value) || (qx.core.Environment.get(name) == value);
		},
		
		
		/**
		 * Returns the value of the given field
		 *
		 * @param name {String} Name of the field to query
		 * @return {var} The value of the given field
		 */		
		getValue : function(name) {
                        var r = jasy.Env.getValue(name);
                        if (r == undefined || r == null) {
			  if (qx && qx.core && qx.core.Environment) {
                            r = qx.core.Environment.get(name);
			  }
                        }
			return r;
		}
	});
})(this);

