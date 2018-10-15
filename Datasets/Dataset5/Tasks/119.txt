return getPackageName(type) + methodName.substring(0, 1).toUpperCase()

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
package org.eclipse.jst.ws.internal.jaxws.core.annotations.initialization;

import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.OPERATION_NAME;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.RESPONSE_SUFFIX;

import java.util.Locale;

import javax.jws.WebMethod;

import org.eclipse.jdt.core.IAnnotation;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.internal.jaxws.core.JAXWSCorePlugin;

/**
 * 
 * @author sclarke
 *
 */
public class ResponseWrapperAttributeInitializer extends RequestWrapperAttributeInitializer {

    @Override
    protected String getClassName(IType type, IMethod method) {
        try {
            String methodName = method.getElementName() + RESPONSE_SUFFIX;
            return getPackageName(type) + methodName.substring(0, 1).toUpperCase(Locale.getDefault())
                + methodName.substring(1) + AnnotationUtils.accountForOverloadedMethods(type, method);
        } catch (JavaModelException jme) {
            JAXWSCorePlugin.log(jme.getStatus());
        }
        return "";
    }
    
    @Override
    protected String getLocalName(IType type, IMethod method) {
        try {
            IAnnotation annotation = AnnotationUtils.getAnnotation(method, WebMethod.class);
            if (annotation != null) {
                String operationName = AnnotationUtils.getStringValue(annotation, OPERATION_NAME);
                if (operationName != null) {
                    return operationName + RESPONSE_SUFFIX;
                }
            }
            return method.getElementName() + RESPONSE_SUFFIX 
                    + AnnotationUtils.accountForOverloadedMethods(type, method);
        } catch (JavaModelException jme) {
            JAXWSCorePlugin.log(jme.getStatus());
        }
        return "";
    }
    
}