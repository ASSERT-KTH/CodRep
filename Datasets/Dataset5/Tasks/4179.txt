printFixableError(annotationMirror.getPosition(),

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

import javax.jws.HandlerChain;

import org.eclipse.jst.ws.annotations.core.processor.AbstractAnnotationProcessor;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.internal.jaxws.core.JAXWSCoreMessages;

import com.sun.mirror.declaration.AnnotationMirror;
import com.sun.mirror.declaration.AnnotationTypeDeclaration;
import com.sun.mirror.declaration.Declaration;
import com.sun.mirror.declaration.FieldDeclaration;
import com.sun.mirror.declaration.MethodDeclaration;
import com.sun.mirror.declaration.TypeDeclaration;

public class HandlerChainRules extends AbstractAnnotationProcessor {

    @Override
    public void process() {
        AnnotationTypeDeclaration annotationDeclaration = (AnnotationTypeDeclaration) environment
                .getTypeDeclaration(HandlerChain.class.getName());

        Collection<Declaration> annotatedTypes = environment
                .getDeclarationsAnnotatedWith(annotationDeclaration);

        for (Declaration declaration : annotatedTypes) {
            if (declaration instanceof TypeDeclaration) {
                @SuppressWarnings("deprecation")
                AnnotationMirror annotationMirror = AnnotationUtils.getAnnotation(declaration,
                        javax.jws.soap.SOAPMessageHandlers.class);
                if (annotationMirror != null) {
                    printError(annotationMirror.getPosition(),
                            JAXWSCoreMessages.HANDLER_CHAIN_SOAP_MESSAGE_HANDLERS);
                }
            }

            if (declaration instanceof FieldDeclaration) {
                AnnotationMirror annotationMirror = AnnotationUtils.getAnnotation(declaration,
                        javax.jws.HandlerChain.class);
                printError(annotationMirror.getPosition(),
                        JAXWSCoreMessages.HANDLER_CHAIN_ON_FIELD);
            }

            if (declaration instanceof MethodDeclaration) {
                AnnotationMirror annotationMirror = AnnotationUtils.getAnnotation(declaration,
                        javax.jws.HandlerChain.class);

                printError(annotationMirror.getPosition(),
                        JAXWSCoreMessages.HANDLER_CHAIN_ON_METHOD);
            }
        }
    }

}