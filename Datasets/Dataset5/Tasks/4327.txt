public interface IResourceID extends ID {

package org.eclipse.ecf.core.identity;

import java.net.URI;

/**
 * Resource id.  ID instances that implement this interface
 * are expected to be resources (files, directories, URLs, etc)
 * and so can be identified via a {@link URI}.
 * 
 */
public interface IResourceID {

	/**
	 * Convert this resource ID to a {@link URI}.
	 * @return URI for this resource ID
	 */
	public URI toURI();

}