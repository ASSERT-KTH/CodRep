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

import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.CLASS_NAME;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.DOT_CHARACTER;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.JAXWS_SUBPACKAGE;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.LOCAL_NAME;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.OPERATION_NAME;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.TARGET_NAMESPACE;

import java.lang.annotation.Annotation;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import javax.jws.WebMethod;
import javax.jws.WebService;

import org.eclipse.jdt.core.IAnnotation;
import org.eclipse.jdt.core.IJavaElement;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.MemberValuePair;
import org.eclipse.jface.text.contentassist.ICompletionProposal;
import org.eclipse.jst.ws.annotations.core.AnnotationsCore;
import org.eclipse.jst.ws.annotations.core.initialization.AnnotationAttributeInitializer;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.internal.jaxws.core.JAXWSCorePlugin;
import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;

/**
 * 
 * @author sclarke
 *
 */
public class RequestWrapperAttributeInitializer extends AnnotationAttributeInitializer {

    @Override
    public List<MemberValuePair> getMemberValuePairs(IJavaElement javaElement, AST ast,
            Class<? extends Annotation> annotationClass) {
        List<MemberValuePair> memberValuePairs = new ArrayList<MemberValuePair>();
        if (javaElement.getElementType() == IJavaElement.METHOD) {
            IMethod method = (IMethod) javaElement;
            IType type = method.getCompilationUnit().findPrimaryType();

            MemberValuePair classNameValuePair = AnnotationsCore.createStringMemberValuePair(ast, CLASS_NAME,
                    getClassName(type, method));

            MemberValuePair localNameValuePair = AnnotationsCore.createStringMemberValuePair(ast, LOCAL_NAME,
                    getLocalName(type, method));

            MemberValuePair targetNamespaceValuePair = AnnotationsCore.createStringMemberValuePair(ast,
                    TARGET_NAMESPACE, getTargetNamespace(type));

            memberValuePairs.add(classNameValuePair);
            memberValuePairs.add(localNameValuePair);
            memberValuePairs.add(targetNamespaceValuePair);
        }
        return memberValuePairs;
    }
    
    public List<ICompletionProposal> getCompletionProposalsForMemberValuePair(IJavaElement javaElement,
            MemberValuePair memberValuePair) {
        
        List<ICompletionProposal> completionProposals = new ArrayList<ICompletionProposal>();
        if (javaElement.getElementType() == IJavaElement.METHOD) {
            IMethod method = (IMethod) javaElement;
            IType type = method.getCompilationUnit().findPrimaryType();

            String memberValuePairName = memberValuePair.getName().getIdentifier();

            if (memberValuePairName.equals(CLASS_NAME)) {
                completionProposals.add(AnnotationUtils.createCompletionProposal(getClassName(type, method),
                        memberValuePair.getValue()));
            }
            if (memberValuePairName.equals(LOCAL_NAME)) {
                completionProposals.add(AnnotationUtils.createCompletionProposal(getLocalName(type, method),
                        memberValuePair.getValue()));
            }
            if (memberValuePairName.equals(TARGET_NAMESPACE)) {
                completionProposals.add(AnnotationUtils.createCompletionProposal(getTargetNamespace(type),
                        memberValuePair.getValue()));
            }
        }
        return completionProposals;
    }
    
    protected String getPackageName(IType type) {
        StringBuilder packageName = new StringBuilder(type.getPackageFragment().getElementName());
        if (packageName.length() > 0) {
            packageName.append(DOT_CHARACTER);               
        }
        packageName.append(JAXWS_SUBPACKAGE);
        packageName.append(DOT_CHARACTER);
        return packageName.toString();
    }
    
    protected String getClassName(IType type, IMethod method) {
        try {
            String methodName = method.getElementName();
            return getPackageName(type) + methodName.substring(0, 1).toUpperCase(Locale.getDefault())
                + methodName.substring(1) + AnnotationUtils.accountForOverloadedMethods(type, method);
        } catch (JavaModelException jme) {
            JAXWSCorePlugin.log(jme.getStatus());
        }
        return "";
    }
    
    protected String getLocalName(IType type, IMethod method) {
        try {
            IAnnotation annotation = AnnotationUtils.getAnnotation(method, WebMethod.class);
            if (annotation != null) {
                String operationName = AnnotationUtils.getStringValue(annotation, OPERATION_NAME);
                if (operationName != null) {
                    return operationName;
                }
            }
            return method.getElementName() + AnnotationUtils.accountForOverloadedMethods(type, method);
        } catch (JavaModelException jme) {
            JAXWSCorePlugin.log(jme.getStatus());
        }
        return "";
    }
    
    protected String getTargetNamespace(IType type) {
        try {
            IAnnotation annotation = AnnotationUtils.getAnnotation(type, WebService.class);
            if (annotation != null) {
                String targetNamespace = AnnotationUtils.getStringValue(annotation, TARGET_NAMESPACE);
                if (targetNamespace != null && targetNamespace.length() > 0) {
                    return targetNamespace;
                }
            }
            return JDTUtils.getTargetNamespaceFromPackageName(type.getPackageFragment().getElementName());
        } catch (JavaModelException jme) {
            JAXWSCorePlugin.log(jme.getStatus());
        }
        return "";
    }

}