printFixableError(mirror.getPosition(), JAXWSCoreMessages

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

import javax.jws.WebService;
import javax.xml.ws.WebServiceProvider;

import org.eclipse.jst.ws.annotations.core.processor.AbstractAnnotationProcessor;
import org.eclipse.jst.ws.internal.jaxws.core.JAXWSCoreMessages;

import com.sun.mirror.declaration.AnnotationMirror;
import com.sun.mirror.declaration.AnnotationTypeDeclaration;
import com.sun.mirror.declaration.Declaration;

public class WebServiceWebServiceProviderCoExistRule extends AbstractAnnotationProcessor {
    
    @Override
    public void process() {
        AnnotationTypeDeclaration annotationDeclaration = (AnnotationTypeDeclaration) environment
                .getTypeDeclaration(WebService.class.getName());

        Collection<Declaration> annotatedTypes = environment
                .getDeclarationsAnnotatedWith(annotationDeclaration);

        for (Declaration declaration : annotatedTypes) {
            Collection<AnnotationMirror> annotationMirrors = declaration.getAnnotationMirrors();

            for (AnnotationMirror mirror : annotationMirrors) {
                checkWebServiceProvider(mirror);
            }
        }
    }

    private void checkWebServiceProvider(AnnotationMirror mirror) {
        if (mirror.getAnnotationType().toString().equals(WebServiceProvider.class.getName())) {
            printError(mirror.getPosition(), JAXWSCoreMessages
                    .WEBSERVICE_WEBSERVICEPROVIDER_COMBINATION);
        }
    }
}