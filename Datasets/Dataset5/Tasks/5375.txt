return new PolymorphicResolver (new QualifiedName ("operatorPlus")).getBestFitCandidates (fdc.findFunctionCandidates (new QualifiedName ("operatorPlus"), fdc.typesForParameters(createEmptyExecutionContext().getTypesystem(), Arrays.asList (params)), false));

/*
Copyright (c) 2008 Arno Haase, André Arnold.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
    André Arnold
 */
package org.eclipse.xtend.backend.functions;

import static org.eclipse.xtend.backend.testhelpers.BackendTestHelper.createEmptyExecutionContext;
import static org.eclipse.xtend.backend.testhelpers.BackendTestHelper.createEmptyFdc;
import static org.junit.Assert.assertEquals;

import java.util.Arrays;
import java.util.Collection;

import org.eclipse.xtend.backend.common.Function;
import org.eclipse.xtend.backend.common.QualifiedName;
import org.eclipse.xtend.backend.functions.internal.FunctionDefContextImpl;
import org.eclipse.xtend.backend.functions.internal.PolymorphicResolver;
import org.eclipse.xtend.backend.types.CompositeTypesystem;
import org.junit.Test;

/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 * @author André Arnold
 */
public class PolymorphicResolverTest {
    @Test public void testWithoutGuards () {
        // this test relies on there being five syslib implementations of operatorPlus - four for the
        //  combinations of Long and Double, and one for Object and Object
        assertEquals (1, getCandidates (2L, 2.0).size());
        assertEquals (1, getCandidates (2.0, 2L).size());
        
        assertEquals (1, getCandidates ("a", "b").size ());
        
        assertEquals (2, getCandidates (null, 2.0).size ());
        assertEquals (2, getCandidates (2.0, null).size ());
        assertEquals (2, getCandidates (null, 2L).size ());
        assertEquals (2, getCandidates (2L, null).size ());
        assertEquals (4, getCandidates (null, null).size ());
        
        assertEquals (1, getCandidates (null, "a").size ());
        assertEquals (1, getCandidates ("a", null).size ());
    }
    
    private Collection<Function> getCandidates (Object... params) {
        final FunctionDefContextImpl fdc = (FunctionDefContextImpl) createEmptyFdc (new CompositeTypesystem ());
        return new PolymorphicResolver (new QualifiedName ("operatorPlus")).getBestFitCandidates (fdc.findFunctionCandidates (new QualifiedName ("operatorPlus"), fdc.typesForParameters(createEmptyExecutionContext().getTypesystem(), Arrays.asList (params))));
    }
    
    //TODO test resolution with guards
}