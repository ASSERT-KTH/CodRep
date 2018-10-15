return JAXWSCoreMessages.WEBMETHOD_ONLY_ON_PUBLIC_METHODS;

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
public class WebMethodNoPrivateMethodRuleTest extends AbstractWebMethodPublicStaticFinalRuleTest {

    @Override
    public IMethod getMethodToTeset() {
        return source.findPrimaryType().getMethod("myPrivateMethod", new String[0]);
    }

    @Override
    public String getErrorMessage() {
        return JAXWSCoreMessages.WEBMETHOD_ONLY_ON_PUBLIC_METHODS_MESSAGE;
    }

}