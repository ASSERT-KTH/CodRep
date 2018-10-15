import static org.eclipse.xtend.backend.testhelpers.BackendTestHelper.*;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.common;

import static org.eclipse.xtend.backend.helpers.BackendTestHelper.*;
import static org.junit.Assert.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.junit.Test;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public class ExpressionBaseTest {
    @Test public void testExecutionListener () {
        final List<String> log = new ArrayList<String> ();
    
        final ExpressionBase expr = createLiteral ("a");

        expr.registerExecutionListener (new ExecutionListener () {
            public void preExecute (ExecutionContext ctx) {
                log.add ("preFirst");
            }

            public void postExecute (Object result, ExecutionContext ctx) {
                log.add ("postFirst");
            }
        });
        expr.registerExecutionListener (new ExecutionListener () {
            public void preExecute (ExecutionContext ctx) {
                log.add ("preSecond");
            }
            
            public void postExecute (Object result, ExecutionContext ctx) {
                log.add ("postSecond");
            }
        });
        
        expr.evaluate (createEmptyExecutionContext());
        
        assertEquals (Arrays.asList ("preFirst", "preSecond", "postSecond", "postFirst"), log);
    }
}