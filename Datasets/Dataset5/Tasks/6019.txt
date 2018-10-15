import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;

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
package org.eclipse.jst.ws.internal.jaxws.ui.views;

import java.lang.reflect.Method;
import java.util.List;

import org.eclipse.jdt.core.IAnnotatable;
import org.eclipse.jdt.core.IAnnotation;
import org.eclipse.jdt.core.IJavaElement;
import org.eclipse.jdt.core.IMemberValuePair;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jdt.core.dom.BooleanLiteral;
import org.eclipse.jdt.core.dom.IExtendedModifier;
import org.eclipse.jdt.core.dom.MemberValuePair;
import org.eclipse.jdt.core.dom.NormalAnnotation;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jdt.core.dom.StringLiteral;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jst.ws.internal.jaxws.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.internal.jaxws.ui.JAXWSUIPlugin;
import org.eclipse.swt.graphics.Image;

/**
 * 
 * @author sclarke
 *
 */
public class AnnotationsValuesColumnLabelProvider extends ColumnLabelProvider {
    private TreeViewer annotationTreeViewer;
    private Image true_image;
    private Image false_image;
    
    public AnnotationsValuesColumnLabelProvider(TreeViewer annotationTreeViewer) {
        this.annotationTreeViewer = annotationTreeViewer;
        true_image = JAXWSUIPlugin.imageDescriptorFromPlugin(JAXWSUIPlugin.PLUGIN_ID, "icons/obj16/true.gif") //$NON-NLS-1$
                .createImage();
        false_image = JAXWSUIPlugin.imageDescriptorFromPlugin(JAXWSUIPlugin.PLUGIN_ID, "icons/obj16/false.gif") //$NON-NLS-1$
                .createImage();
    }
    
    @Override
    public String getText(Object element) {
        String text = ""; //$NON-NLS-1$
        if (element instanceof Method) {
            text =  getTextForMethod((Method)element);
        }
        return text;
    }
    
    private String getTextForMethod(Method method) {
        String text = ""; //$NON-NLS-1$
        if (annotationTreeViewer.getInput() instanceof IAnnotatable) {
            text = getTextForMethod(method, (IAnnotatable) annotationTreeViewer.getInput());
        } else if (annotationTreeViewer.getInput() instanceof SingleVariableDeclaration) {
            text = getTextForMethod(method, (SingleVariableDeclaration)annotationTreeViewer.getInput());
        }
        return text;
    }

    private String getTextForMethod(Method method, IAnnotatable annotatedElement) {
        Class<?> returnType = method.getReturnType();
        try {
            IAnnotation[] annotations = annotatedElement.getAnnotations();
            for (IAnnotation annotation : annotations) {
                Class<?> declaringClass = method.getDeclaringClass();
                if (annotation.getElementName().equals(declaringClass.getSimpleName())
                        || annotation.getElementName().equals(declaringClass.getCanonicalName())) {
                    IMemberValuePair[] memberValuePairs = annotation.getMemberValuePairs();
                    for (IMemberValuePair memberValuePair : memberValuePairs) {
                        if (memberValuePair.getMemberName().equals(method.getName())) {
                            if (returnType.equals(String.class)) {
                                return memberValuePair.getValue().toString();
                            }
                            
                            if (returnType.equals(Class.class)) {
                                return memberValuePair.getValue().toString() + ".class";  //$NON-NLS-1$
                            }
                            if (returnType.isPrimitive() && (returnType.equals(Byte.TYPE) 
                                    || returnType.equals(Short.TYPE) 
                                    || returnType.equals(Integer.TYPE) || returnType.equals(Long.TYPE)
                                    || returnType.equals(Float.TYPE) 
                                    || returnType.equals(Double.TYPE))) {
                                return memberValuePair.getValue().toString();
                            }
                            
                            if (returnType.isArray()) {
                                Object[] values = (Object[])memberValuePair.getValue();
                                if (values != null && values.length > 0) {
                                    return "[]{...}"; //$NON-NLS-1$
                                } else {
                                    return "[]{}"; //$NON-NLS-1$
                                }
                            }
                            
                            if (returnType.isEnum()) {
                                String enumValue = memberValuePair.getValue().toString();
                                return enumValue.substring(enumValue.lastIndexOf(".") + 1); //$NON-NLS-1$
                            }
                        }
                    }
                }
            }
        } catch (JavaModelException jme) {
            JAXWSUIPlugin.log(jme.getStatus());
        }
        return ""; //$NON-NLS-1$
    }

    @SuppressWarnings("unchecked")
    private String getTextForMethod(Method method, SingleVariableDeclaration singleVariableDeclaration) {
        Class<?> returnType = method.getReturnType();
        List<IExtendedModifier> modifiers = singleVariableDeclaration.modifiers();
        for (IExtendedModifier extendedModifier : modifiers) {
            if (extendedModifier instanceof NormalAnnotation) {
                NormalAnnotation normalAnnotation = (NormalAnnotation) extendedModifier;
                String annotationName = AnnotationUtils.getAnnotationName(normalAnnotation);
                Class<?> declaringClass = method.getDeclaringClass();
                if (annotationName.equals(declaringClass.getSimpleName()) || 
                        annotationName.equals(declaringClass.getCanonicalName())) {
                    List<MemberValuePair> memberValuePairs = normalAnnotation.values();
                    for (MemberValuePair memberValuePair : memberValuePairs) {
                        if (memberValuePair.getName().toString().equals(method.getName())) {
                            if (returnType.equals(String.class)) {
                                StringLiteral stringLiteral = (StringLiteral)memberValuePair.getValue();
                                return stringLiteral.getLiteralValue();
                            }

                            if (returnType.isPrimitive() && (returnType.equals(Byte.TYPE) 
                                    || returnType.equals(Short.TYPE) 
                                    || returnType.equals(Integer.TYPE) || returnType.equals(Long.TYPE)
                                    || returnType.equals(Float.TYPE) 
                                    || returnType.equals(Double.TYPE))) {
                                return memberValuePair.getValue().toString();
                            }

                            if (returnType.isEnum()) {
                                String enumValue = memberValuePair.getValue().toString();
                                return enumValue.substring(enumValue.lastIndexOf(".") + 1); //$NON-NLS-1$
                            }
                        }
                    }
                }
            }
        }
        return ""; //$NON-NLS-1$
    }
    
    @Override
    public Image getImage(Object element) {
        try {
            if (element instanceof Class) {
                return getImageForClass((Class<?>) element);
            }
            if (element instanceof Method) {
                return getImageForMethod((Method) element);
            }
        } catch (JavaModelException jme) {
            JAXWSUIPlugin.log(jme.getStatus());
        }
        return null;
    }
        
    private Image getImageForClass(Class<?> aClass) throws JavaModelException {
        if (annotationTreeViewer.getInput() instanceof IAnnotatable) {
            return getImageForClass(aClass, (IAnnotatable) annotationTreeViewer.getInput());
        }
        
        if (annotationTreeViewer.getInput() instanceof SingleVariableDeclaration) {
            return getImageForClass(aClass, (SingleVariableDeclaration)annotationTreeViewer.getInput());
        }
        return false_image;        
    }
    
    private Image getImageForClass(Class<?> aClass, IAnnotatable annotatedElement) throws JavaModelException {
        IAnnotation[] annotations = annotatedElement.getAnnotations();
        for (IAnnotation annotation : annotations) {
            String annotationName = annotation.getElementName();
            if (AnnotationUtils.isAnnotationPresent((IJavaElement)annotatedElement, annotationName) && 
                    (annotationName.equals(aClass.getSimpleName()) || 
                    annotationName.equals(aClass.getCanonicalName()))) {
                return true_image;
            }
        }
        return false_image;
    }
    
    @SuppressWarnings("unchecked")
    private Image getImageForClass(Class<?> aClass, SingleVariableDeclaration parameter) {
        List<IExtendedModifier> modifiers = parameter.modifiers();
        for (IExtendedModifier extendedModifier : modifiers) {
            if (extendedModifier instanceof Annotation) {
                Annotation annotation = (Annotation) extendedModifier;
                String annotationName = AnnotationUtils.getAnnotationName(annotation);
                if (AnnotationUtils.isAnnotationPresent(parameter, annotation)
                        && (annotationName.equals(aClass.getSimpleName())
                        || annotationName.equals(aClass.getCanonicalName()))) {
                    return true_image;
                }
            }
        }
        return false_image;
    }
    
    private Image getImageForMethod(Method method) throws JavaModelException {
        Class<?> returnType = method.getReturnType();
        if (returnType.equals(Boolean.TYPE)) {
            if (annotationTreeViewer.getInput() instanceof IAnnotatable) {
                return getImageForMethod(method, (IAnnotatable) annotationTreeViewer.getInput());
            }
            if (annotationTreeViewer.getInput() instanceof SingleVariableDeclaration) {
                return getImageForMethod(method, (SingleVariableDeclaration)annotationTreeViewer.getInput());
            }
        }
        return null;
    }

    private Image getImageForMethod(Method method, IAnnotatable annotatedElement) throws JavaModelException {
        IAnnotation[] annotations = annotatedElement.getAnnotations();
        for (IAnnotation annotation : annotations) {
            String annotationName = annotation.getElementName();
            Class<?> declaringClass = method.getDeclaringClass();
            if (annotationName.equals(declaringClass.getSimpleName())
                    || annotationName.equals(declaringClass.getCanonicalName())) {
                IMemberValuePair[] memberValuePairs = annotation.getMemberValuePairs();
                for (IMemberValuePair memberValuePair : memberValuePairs) {
                    if (memberValuePair.getMemberName().equals(method.getName())) {
                        if (Boolean.parseBoolean(memberValuePair.getValue().toString())) {
                            return true_image;
                        }
                    }
                }
            }
        }
        return false_image;
    }
    
    @SuppressWarnings("unchecked")
    private Image getImageForMethod(Method method, SingleVariableDeclaration singleVariableDeclaration) 
            throws JavaModelException {
        List<IExtendedModifier> modifiers = singleVariableDeclaration.modifiers();
        for (IExtendedModifier extendedModifier : modifiers) {
            if (extendedModifier instanceof NormalAnnotation) {
                NormalAnnotation annotation = (NormalAnnotation) extendedModifier;
                String annotationName = AnnotationUtils.getAnnotationName(annotation);
                Class<?> declaringClass = method.getDeclaringClass();
                if (annotationName.equals(declaringClass.getSimpleName())
                        || annotationName.equals(declaringClass.getCanonicalName())) {
                    List<MemberValuePair> memberValuePairs = annotation.values();
                    for (MemberValuePair memberValuePair : memberValuePairs) {
                        if (memberValuePair.getName().toString().equals(method.getName())) {
                            BooleanLiteral booleanLiteral = (BooleanLiteral)memberValuePair.getValue();
                            if (booleanLiteral.booleanValue()) {
                                return true_image;
                            }
                        }
                    }
                }
            }
        }
        return false_image;
    }

    @Override
    public void dispose() {
        super.dispose();
        true_image.dispose();
        false_image.dispose();
    }
}