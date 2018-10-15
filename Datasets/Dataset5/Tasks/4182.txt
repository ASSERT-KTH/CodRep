printFixableError(declaration.getPosition(),

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

import org.eclipse.jst.ws.annotations.core.processor.AbstractAnnotationProcessor;
import org.eclipse.jst.ws.internal.jaxws.core.JAXWSCoreMessages;

import com.sun.mirror.declaration.AnnotationMirror;
import com.sun.mirror.declaration.AnnotationTypeDeclaration;
import com.sun.mirror.declaration.ClassDeclaration;
import com.sun.mirror.declaration.ConstructorDeclaration;
import com.sun.mirror.declaration.Declaration;
import com.sun.mirror.declaration.Modifier;

public class WebServiceDefaultPublicConstructorRule extends AbstractAnnotationProcessor {

    @Override
    public void process() {
        AnnotationTypeDeclaration annotationDeclaration = (AnnotationTypeDeclaration) environment
                .getTypeDeclaration(WebService.class.getName());

        Collection<Declaration> annotatedTypes = environment
                .getDeclarationsAnnotatedWith(annotationDeclaration);

        for (Declaration declaration : annotatedTypes) {
            if (declaration instanceof ClassDeclaration) {
                boolean hasDefaultConstructor = false;
                ClassDeclaration classDeclaration = (ClassDeclaration) declaration;
                Collection<ConstructorDeclaration> constructors = classDeclaration.getConstructors();
                if (constructors.size() == 0) {
                    hasDefaultConstructor = true;
                } else {
                    for (ConstructorDeclaration constructorDeclaration : constructors) {
                        if (constructorDeclaration.getModifiers().contains(Modifier.PUBLIC) && 
                                constructorDeclaration.getParameters().size() == 0) {
                            hasDefaultConstructor = true;
                            break;
                        }
                    }
                }
                if (!hasDefaultConstructor) {
                    Collection<AnnotationMirror> annotationMirrors = declaration.getAnnotationMirrors();
                    for (AnnotationMirror mirror : annotationMirrors) {
                        if ( mirror.getAnnotationType().toString().equals(annotationDeclaration
                                .getQualifiedName())) {
                            printError(mirror.getPosition(),
                                    JAXWSCoreMessages.WEBSERVICE_DEFAULT_PUBLIC_CONSTRUCTOR); 
                        }
                    }
                }                
            }
        }
    }

}