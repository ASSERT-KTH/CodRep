public static CompositeTypesystem createJustEmf () {

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipose.xtend.middleend;

import java.util.List;

import org.eclipse.xtend.backend.common.BackendTypesystem;
import org.eclipse.xtend.backend.types.CompositeTypesystem;
import org.eclipse.xtend.backend.types.emf.EmfTypesystem;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class BackendTypesystemFactory {
    
    /**
     * This generic factory requires the caller to provide a complete list of typesystems that
     *  will comprise the actual typesystem. The ordering in this list is semantically
     *  relevant because types are searched from beginning to end.
     */
    public static CompositeTypesystem create (List<? extends BackendTypesystem> typesystems) {
        final CompositeTypesystem result = new CompositeTypesystem ();
        
        for (BackendTypesystem ts: typesystems)
            result.register(ts);
         
        return result;
    }

    /**
     * This is a convenience factory method to create a typesystem that supports both EMF
     *  and Java Beans. UML is left out for performance reasons - the UML metamodel requires
     *  the UML metamodel to be parsed initially which takes significant time.
     */
    public static CompositeTypesystem createWithoutUml () {
        final CompositeTypesystem result = new CompositeTypesystem ();

        result.register (new EmfTypesystem ());

        return result;
    }
}
