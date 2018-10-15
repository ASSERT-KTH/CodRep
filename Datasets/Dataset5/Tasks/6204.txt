processMethod(methodDeclaration);

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

import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.HEADER;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.MODE;

import java.util.Collection;

import javax.jws.Oneway;
import javax.jws.WebParam;
import javax.jws.WebParam.Mode;
import javax.jws.soap.SOAPBinding;
import javax.xml.ws.Holder;

import org.eclipse.jst.ws.annotations.core.processor.AbstractAnnotationProcessor;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.internal.jaxws.core.JAXWSCoreMessages;
import org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils;

import com.sun.mirror.declaration.AnnotationMirror;
import com.sun.mirror.declaration.AnnotationTypeDeclaration;
import com.sun.mirror.declaration.Declaration;
import com.sun.mirror.declaration.MethodDeclaration;
import com.sun.mirror.declaration.ParameterDeclaration;
import com.sun.mirror.declaration.TypeDeclaration;
import com.sun.mirror.type.TypeMirror;

public class SOAPBindingDocumentBareRules extends AbstractAnnotationProcessor {
    
    @Override
    public void process() {
        AnnotationTypeDeclaration annotationDeclaration = (AnnotationTypeDeclaration) environment
        .getTypeDeclaration(SOAPBinding.class.getName());

        Collection<Declaration> annotatedTypes = environment
                .getDeclarationsAnnotatedWith(annotationDeclaration);
        
        for (Declaration declaration : annotatedTypes) {
            if (declaration instanceof TypeDeclaration) {
                TypeDeclaration typeDeclaration = (TypeDeclaration) declaration;
                Collection<AnnotationMirror> annotationMirrors = typeDeclaration.getAnnotationMirrors();
                for (AnnotationMirror mirror : annotationMirrors) {
                    if (mirror.getAnnotationType().getDeclaration().equals(annotationDeclaration)) {
                        if (JAXWSUtils.isDocumentBare(mirror)) {
                            Collection<? extends MethodDeclaration> methodDeclarations = typeDeclaration.getMethods();
                            for (MethodDeclaration methodDeclaration : methodDeclarations) {
                                processMethod(methodDeclaration);    
                            }
                        }
                    }
                }
            }
            
            if (declaration instanceof MethodDeclaration) {
                MethodDeclaration methodDeclaration = (MethodDeclaration) declaration;
                Collection<AnnotationMirror> annotationMirrors = methodDeclaration.getAnnotationMirrors();
                for (AnnotationMirror mirror : annotationMirrors) {
                    if (mirror.getAnnotationType().getDeclaration().equals(annotationDeclaration)) {
                        if (JAXWSUtils.isDocumentBare(mirror)) {
                            processMethod((MethodDeclaration) declaration);
                        }
                    }
                }
            }
        }
    }

    public void processMethod(MethodDeclaration methodDeclaration) {
        Collection<ParameterDeclaration> parameters = methodDeclaration.getParameters();
        
        //@Oneway operations
        if (isOneway(methodDeclaration) && !isSingleNonHeaderINParameter(parameters)) {
            printError(methodDeclaration.getPosition(), 
                JAXWSCoreMessages.DOC_BARE_ONLY_ONE_NON_HEADER_IN_PARAMETER);                                
        } else {
            if (isVoidReturnType(methodDeclaration)) {
                if (countINParameters(parameters) > 1) {
                    printError(methodDeclaration.getPosition(), 
                            JAXWSCoreMessages.DOC_BARE_VOID_RETURN_ONE_IN_PARAMETER);                                                                        
                }
                if (countOUTParameters(parameters) > 1) {
                    printError(methodDeclaration.getPosition(), 
                            JAXWSCoreMessages.DOC_BARE_VOID_RETURN_ONE_OUT_PARAMETER);                                                                                            
                }
            } else {
                if (countINParameters(parameters) > 1) {
                    printError(methodDeclaration.getPosition(), 
                        JAXWSCoreMessages.DOC_BARE_ONLY_ONE_NON_HEADER_IN_PARAMETER);                                                                        
                } 
                if (countOUTParameters(parameters) > 0) {
                    printError(methodDeclaration.getPosition(), 
                        JAXWSCoreMessages.DOC_BARE_NON_VOID_RETURN_NO_INOUT_OUT_PARAMETER);
                }
            }
        }

        //check for @WebParam.name attribute when @WebParam.Mode = OUT or INOUT
//        for(ParameterDeclaration parameterDeclaration : parameters) {
//            AnnotationMirror annotationMirror = AnnotationUtils.getAnnotation(parameterDeclaration, WebParam.class);
//            if (annotationMirror != null) {
//                String mode = getWebParamMode(annotationMirror, parameterDeclaration);
//                String name = AnnotationUtils.getStringValue(annotationMirror, NAME);
//                
//                if (name == null && (mode.equals(Mode.OUT.name()) || mode.equals(Mode.INOUT.name()))) {
//                    printError(annotationMirror.getPosition(), 
//                       JAXWSCoreMessages.WEBPARAM_NAME_REQUIRED_WHEN_DOC_BARE_OUT_INOUT);
//                }
//            }
//        }
    }
    
    private boolean isOneway(MethodDeclaration methodDeclaration) {
        AnnotationMirror oneway = AnnotationUtils.getAnnotation(methodDeclaration, Oneway.class);
        if (oneway != null) {
            return true;
        }
        return false;
    }
    
    private boolean isVoidReturnType(MethodDeclaration methodDeclaration) {
        return methodDeclaration.getReturnType().equals(environment.getTypeUtils().getVoidType());
    }
    
    private boolean isSingleNonHeaderINParameter(Collection<ParameterDeclaration> parameters) {
        return countNonHeaderINParameters(parameters) <= 1;
    }
    
    private int countNonHeaderINParameters(Collection<ParameterDeclaration> parameters) {
        int inNonHeaderParameters = 0;
        for (ParameterDeclaration parameterDeclaration : parameters) {
            if (isNonHeaderINParameter(parameterDeclaration)) {
                inNonHeaderParameters++;
            }
        }
        return inNonHeaderParameters;
    }
    
    private boolean isNonHeaderINParameter(ParameterDeclaration parameterDeclaration) {
        AnnotationMirror webParam = AnnotationUtils.getAnnotation(parameterDeclaration, WebParam.class);
        if (webParam != null) {
            return getWebParamMode(webParam, parameterDeclaration).equals(Mode.IN.name())
              && !isHeader(webParam);
        }
        
        if (getDefaultWebParamMode(parameterDeclaration).equals(Mode.IN.name())) {
            return true;
        }
        
        return false;
    }
    
    private int countINParameters(Collection<ParameterDeclaration> parameters) {
        int inNonHeaderParameters = 0;
        for (ParameterDeclaration parameterDeclaration : parameters) {
            if (isINParameter(parameterDeclaration)) {
                inNonHeaderParameters++;
            }
        }
        return inNonHeaderParameters;
    }
 
    private boolean isINParameter(ParameterDeclaration parameterDeclaration) {
        AnnotationMirror webParam = AnnotationUtils.getAnnotation(parameterDeclaration, WebParam.class);
        if (webParam != null) {
            String mode = getWebParamMode(webParam, parameterDeclaration);
            return (mode.equals(Mode.IN.name()) || mode.equals(Mode.INOUT.name()))
                    && !isHeader(webParam);
        }
        
        String defaultMode = getDefaultWebParamMode(parameterDeclaration);
        if (defaultMode.equals(Mode.IN.name()) || defaultMode.equals(Mode.INOUT.name())) {
            return true;
        }

        return false;
    }

    private int countOUTParameters(Collection<ParameterDeclaration> parameters) {
        int outNonHeaderParameters = 0;
        for (ParameterDeclaration parameterDeclaration : parameters) {
            if (isOUTParameter(parameterDeclaration)) {
                outNonHeaderParameters++;
            }
        }
        return outNonHeaderParameters;
    }

    private boolean isOUTParameter(ParameterDeclaration parameterDeclaration) {
        AnnotationMirror webParam = AnnotationUtils.getAnnotation(parameterDeclaration, WebParam.class);
        if (webParam != null) {
            String mode = getWebParamMode(webParam, parameterDeclaration);
            return (mode.equals(Mode.OUT.name()) || mode.equals(Mode.INOUT.name()))
                    && !isHeader(webParam);
        }
        
        if (getDefaultWebParamMode(parameterDeclaration).equals(Mode.INOUT.name())) {
            return true;
        }

        return false;
    }

    private boolean isHeader(AnnotationMirror annotationMirror) {
        Boolean header = AnnotationUtils.getBooleanValue(annotationMirror, HEADER);
        if (header != null) {
           return header.booleanValue();
        }
        return false;
    }
    
    private String getWebParamMode(AnnotationMirror annotationMirror, ParameterDeclaration parameterDeclaration) {
        String mode = AnnotationUtils.getStringValue(annotationMirror, MODE);
        if (mode == null || mode.length() == 0) {
            mode = getDefaultWebParamMode(parameterDeclaration);
        }
        return mode;
    }
    
    private String getDefaultWebParamMode(ParameterDeclaration parameterDeclaration) {
        TypeMirror typeMirror = environment.getTypeUtils().getErasure(parameterDeclaration.getType());
        if (typeMirror.toString().equals(Holder.class.getCanonicalName())) {
            return Mode.INOUT.name();
        }
        return Mode.IN.name();
    }
    
}