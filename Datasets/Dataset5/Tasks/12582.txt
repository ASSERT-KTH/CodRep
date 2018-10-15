package org.apache.wicket.request.resource;

package org.apache.wicket.ng.resource;

/**
 * Represents content disposition of a resource
 * 
 * @author Matej Knopp
 */
public enum ContentDisposition {
	/**
	 * Inline resources are usually displayed within the browser window
	 */
	INLINE,

	/**
	 * For attachment resources the browser should display a save dialog
	 */
	ATTACHMENT;
}
 No newline at end of file