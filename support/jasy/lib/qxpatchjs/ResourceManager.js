/* 
==================================================================================================
  Jasy - JavaScript Tooling Framework
  Copyright 2010-2011 Sebastian Werner
==================================================================================================
*/

/**
 * Contains information about images (size, format, clipping, ...) and
 * other assets like CSS files, local data, ...
 */
(function(global) 
{
	console.log("RESOURCE MANAGER LOADED");
	
	
	Module("qxpatchjs.ResourceManager",
	{
		/**
		 * Whether the registry has information about the given asset.
		 *
		 * @param id {String} The asset to get the information for
		 * @return {Boolean} <code>true</code> when the asset is known.
		 */
		has : function(id) {
			return Asset.has(id);
		},


		/**
		 * Returns the width of the given image ID
		 */
                getImageWidth : function(id)
                {
                        return Asset.getImageSize(id).width;
                },
                
                /**
		 * Returns the height of the given image ID
		 */
                getImageHeight : function(id)
                {
                        return Asset.getImageSize(id).height;
                },
                


		/**
		 * Returns sprite details for being used for the given image ID.
		 *
		 * Nothing is returned when the given ID is not available as part of an image sprite.
		 *
		 * @param id {String} Asset identifier
		 * @return {Map} 
		 */
		getImageSprite : function(id)
		{
			return Asset.getImageSprite(id);
		},


		/**
		 * Converts the given asset ID to a full qualified URI
		 *
		 * @param id {String} Asset ID
		 * @return {String} Resulting URI
		 * @throws when the asset ID is unknown
		 */
		toUri : function(id)
		{
                        return Asset.toUri(id);
		},
                
                getInstance : function()
                {
                        return this;
                },
                
                getCombinedFormat : function(id)
                {
                        return "png"; // TODO
                },
                
                getData : function(id)
                {
                        return null; // TODO
                },
                
                getImageFormat : function(id)
                {
                        return "png";
                },
                
                toDataUri : function(id)
                {
                        return Asset.toUri(id); // TODO
                }
	});	
})(this);