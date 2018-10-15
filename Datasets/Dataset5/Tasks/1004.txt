return JAXWSCoreMessages.ONEWAY_NO_RETURN_VALUE;

/*******************************************************************************
 * Copyright (c) 2009 Shane Clarke.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Shane Clarke - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.jaxws.core.annotation.validation.tests;

import org.eclipse.jdt.core.IMethod;
import org.eclipse.jst.ws.internal.jaxws.core.JAXWSCoreMessages;

/**
 * 
 * @author sclarke
 *
 */
public class OnewayNoReturnValueRuleTest extends AbstractOnewayValidationTest {

	@Override
	public String getClassContents() {
	    StringBuilder classContents = new StringBuilder("package com.example;\n\n");
	    classContents.append("public class MyClass {\n\n\tpublic int myMethod(int i) {\n\t\treturn 0;\n\t}\n}");
        return classContents.toString();
	}

    public String getErrorMessage() {
        return JAXWSCoreMessages.ONEWAY_NO_RETURN_VALUE_ERROR_MESSAGE;
    }

    @Override
    public IMethod getMethodToTest() {
        return source.findPrimaryType().getMethod("myMethod", new String[]{"I"});
    }
    
}