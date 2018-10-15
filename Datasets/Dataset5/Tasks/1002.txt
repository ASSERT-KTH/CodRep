memberValuePairs.add(AnnotationsCore.createTypeMemberValuePair(ast, name,

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
package org.eclipse.jst.ws.annotations.core.initialization;

import java.lang.annotation.Annotation;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.jdt.core.IJavaElement;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.MemberValuePair;
import org.eclipse.jst.ws.annotations.core.AnnotationsCore;

/**
 * Constructs <code>MemberValuePair</code> from the defaults found in the passed in <code>Annotation</code>.
 * <p>
 * <strong>Provisional API:</strong> This class/interface is part of an interim API that is still under 
 * development and expected to change significantly before reaching stability. It is being made available at 
 * this early stage to solicit feedback from pioneering adopters on the understanding that any code that uses 
 * this API will almost certainly be broken (repeatedly) as the API evolves.
 * </p>
 * @author sclarke
 */
public class DefaultsAnnotationAttributeInitializer extends AnnotationAttributeInitializer {
    
    public DefaultsAnnotationAttributeInitializer() {
        
    }

    @Override
    public List<MemberValuePair> getMemberValuePairs(IJavaElement javaElement, AST ast,
            Class<? extends Annotation> annotationClass) {
        return getMemberValuePairs(ast, annotationClass);
    }

    @Override
    public List<MemberValuePair> getMemberValuePairs(ASTNode astNode, AST ast,
            Class<? extends Annotation> annotationClass) {
        return getMemberValuePairs(ast, annotationClass);
    }
    
    private List<MemberValuePair> getMemberValuePairs(AST ast,
            Class<? extends Annotation> annotationClass) {
        List<MemberValuePair> memberValuePairs = new ArrayList<MemberValuePair>();
        
        Method[] declaredMethods = annotationClass.getDeclaredMethods();
        for (Method method : declaredMethods) {
            String name = method.getName();
            Class<?> returnType = method.getReturnType();
            Object defaultValue = method.getDefaultValue();

            if (defaultValue != null) {
                if (returnType.equals(String.class)) {
                    memberValuePairs.add(AnnotationsCore.createStringMemberValuePair(ast,
                            name, defaultValue.toString()));
                }
                
                if (returnType.equals(Boolean.TYPE)) {
                    memberValuePairs.add(AnnotationsCore.createBooleanMemberValuePair(ast,
                            name, Boolean.parseBoolean(defaultValue.toString())));
                }
                
                if (returnType.isPrimitive() && (returnType.equals(Byte.TYPE) || returnType.equals(Short.TYPE) 
                        || returnType.equals(Integer.TYPE) || returnType.equals(Long.TYPE)
                        || returnType.equals(Float.TYPE) || returnType.equals(Double.TYPE))) {
                    memberValuePairs.add(AnnotationsCore.createNumberMemberValuePair(ast, name, defaultValue));
                }
                
                if (returnType.isArray()) {
                    memberValuePairs.add(AnnotationsCore.createArrayMemberValuePair(ast, method, 
                            (Object[])defaultValue));
                }
                
                if (returnType.isEnum()) {
                    memberValuePairs.add(AnnotationsCore.createEnumMemberValuePair(ast, 
                            method.getDeclaringClass().getCanonicalName(), name, defaultValue));
                }
                
                if (returnType.equals(Class.class)) {
                    memberValuePairs.add(AnnotationsCore.createTypeMemberVaulePair(ast, name, 
                            defaultValue));
                }
            }
        }      
        return memberValuePairs;
    }
}