public interface IIdentifiable {

package org.eclipse.ecf.core;

import org.eclipse.ecf.core.identity.ID;

/**
 * Defines implementing classes as being identifiable with
 * an ECF identity.  
 *
 */
public interface IIDentifiable {

    /**
     * Get the ID for this 'identifiable' object
     * @return ID the ID for this identifiable object
     */
    public ID getID();
}