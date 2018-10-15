package org.eclipse.xtend.middleend.plugins;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipose.xtend.middleend.plugins;


/**
 * This interface is the common abstraction through which all handlers for different
 *  languages can contribute their middle ends. Every language should contribute its
 *  MiddleEnd implementation factory through the extension point.
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public interface LanguageSpecificMiddleEndFactory {
    /**
     * a clear text name describing the language / middle end
     */
    String getName ();
    
    /**
     * the priority is a possible way to determine the order in which the middle ends
     *  are asked if they can handle a given resource. Typically, only one middle end
     *  implementation should declare that it can handle a given resource (i.e. source
     *  file), and in this case a priority of 0 should be returned. <br>
     *  
     * In the rare case where it is needed, highest priority is asked first.
     */
    int getPriority ();

    /**
     * This method creates the actual implementation of the middle end. The specificData parameter is 
     *  passed through from the MiddleEnd constructor.<br>
     *  
     * It is permitted for implementations to throw an IllegalArgumentException, 
     *  which is the official way for an implementation to say that it views the 
     *  passed data as insufficient to perform, and therefore needs to be removed
     *  from the list of registered middle ends. This is done on a per-call basis
     *  and avoids the necessity to always initialize all middle end implementations.
     */
    LanguageSpecificMiddleEnd create (Object specificData);
}