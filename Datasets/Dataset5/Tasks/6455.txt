super (computeName (stereoTypeTypes), computeName(stereoTypeTypes), stereoTypeTypes.toArray (new BackendType[0])); //TODO uniqueRepresentation

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.types.uml2.internal;

import java.util.List;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.types.AbstractType;

/**
 * This type is used to support assignment of multiple stereotypes to a
 * model element. Methods from the superclass are overridden to evaluate
 * them for each wrapped stereotype.
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */

public final class MultipleStereotypeType extends AbstractType {
    private final List<BackendType> _stereotypeTypes;
    
    public MultipleStereotypeType (List<BackendType> stereoTypeTypes) {
        super (computeName (stereoTypeTypes), stereoTypeTypes.toArray (new BackendType[0]));
        
        _stereotypeTypes = stereoTypeTypes;
    }

	/** Needed to be called within constructor */
	private static String computeName (List<BackendType> stereotypes) {
		final StringBuilder result = new StringBuilder (stereotypes.get(0).getName());

		for (int i=1; i<stereotypes.size(); i++) 
			result.append ("," + stereotypes.get(i).getName()); 
		
		return result.toString();
	}

    @Override
    public int hashCode () {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((_stereotypeTypes == null) ? 0 : _stereotypeTypes.hashCode());
        return result;
    }

    @Override
    public boolean equals (Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        final MultipleStereotypeType other = (MultipleStereotypeType) obj;
        if (_stereotypeTypes == null) {
            if (other._stereotypeTypes != null)
                return false;
        } else if (!_stereotypeTypes.equals(other._stereotypeTypes))
            return false;
        return true;
    }
}