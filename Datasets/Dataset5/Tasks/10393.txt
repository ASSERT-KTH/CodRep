.WEBSERVICE_WEBSERVICEPROVIDER_COMBINATION_ERROR_MESSAGE);

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
package org.eclipse.jst.ws.internal.jaxws.core.annotations.validation;

import java.util.Collection;

import org.eclipse.jst.ws.annotations.core.processor.AbstractAnnotationProcessor;
import org.eclipse.jst.ws.internal.jaxws.core.JAXWSCoreMessages;

import com.sun.mirror.apt.Messager;
import com.sun.mirror.declaration.AnnotationMirror;
import com.sun.mirror.declaration.AnnotationTypeDeclaration;
import com.sun.mirror.declaration.Declaration;

/**
 * 
 * @author sclarke
 *
 */
public class WebServiceWebServiceProviderCoExistRule extends AbstractAnnotationProcessor {
    
    public WebServiceWebServiceProviderCoExistRule() {
    }
    
    @Override
    public void process() {
        Messager messager = environment.getMessager();

        AnnotationTypeDeclaration annotationDeclaration = (AnnotationTypeDeclaration) environment
                .getTypeDeclaration("javax.jws.WebService"); //$NON-NLS-1$

        Collection<Declaration> annotatedTypes = environment
                .getDeclarationsAnnotatedWith(annotationDeclaration);

        for (Declaration declaration : annotatedTypes) {
            Collection<AnnotationMirror> annotationMirrors = declaration.getAnnotationMirrors();

            for (AnnotationMirror mirror : annotationMirrors) {
                checkWebServiceProvider(mirror, messager);
            }
        }
    }

    private void checkWebServiceProvider(AnnotationMirror mirror, Messager messager) {
        if (mirror.getAnnotationType().toString().equals("javax.xml.ws.WebServiceProvider")) { //$NON-NLS-1$
            messager.printError(mirror.getPosition(), JAXWSCoreMessages
                    .WEBSERVICE_ANNOTATION_PROCESSOR_WEBSERVICE_WEBSERVICEPROVIDER_ERROR_MESSAGE);
        }
    }
}