JAXWSUIPlugin.log(ce.getStatus());

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
import java.util.Collections;
import java.util.List;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.IAnnotatable;
import org.eclipse.jdt.core.IAnnotation;
import org.eclipse.jdt.core.ICompilationUnit;
import org.eclipse.jdt.core.IField;
import org.eclipse.jdt.core.IJavaElement;
import org.eclipse.jdt.core.IMember;
import org.eclipse.jdt.core.IMemberValuePair;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.IPackageDeclaration;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jdt.core.dom.BooleanLiteral;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.IExtendedModifier;
import org.eclipse.jdt.core.dom.MemberValuePair;
import org.eclipse.jdt.core.dom.NormalAnnotation;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.QualifiedName;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jdt.core.dom.StringLiteral;
import org.eclipse.jdt.core.dom.rewrite.ASTRewrite;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.CheckboxCellEditor;
import org.eclipse.jface.viewers.ComboBoxCellEditor;
import org.eclipse.jface.viewers.EditingSupport;
import org.eclipse.jface.viewers.ICellEditorValidator;
import org.eclipse.jface.viewers.TextCellEditor;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jst.ws.annotations.core.AnnotationsCore;
import org.eclipse.jst.ws.annotations.core.AnnotationsManager;
import org.eclipse.jst.ws.annotations.core.initialization.IAnnotationAttributeInitializer;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.internal.jaxws.ui.JAXWSUIMessages;
import org.eclipse.jst.ws.internal.jaxws.ui.JAXWSUIPlugin;
import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;
import org.eclipse.ltk.core.refactoring.Change;
import org.eclipse.ltk.core.refactoring.IUndoManager;
import org.eclipse.ltk.core.refactoring.RefactoringCore;
import org.eclipse.ltk.core.refactoring.RefactoringStatus;
import org.eclipse.ltk.core.refactoring.TextFileChange;
import org.eclipse.ui.IFileEditorInput;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.texteditor.ITextEditor;

/**
 * @author sclarke
 * 
 */
public class AnnotationsValuesEditingSupport extends EditingSupport {
    private AnnotationsView annotationsView;
    private TreeViewer treeViewer;
    
    private TextCellEditor textCellEditor;
    private CheckboxCellEditor checkboxCellEditor;
    private ComboBoxCellEditor comboBoxCellEditor;
    private ClassDialogCellEditor classDialogCellEditor;
    private AnnotationArrayCellEditor annotationArrayCellEditor;

    public AnnotationsValuesEditingSupport(AnnotationsView annotationsView, TreeViewer treeViewer) {
        super(treeViewer);
        this.treeViewer = treeViewer;
        this.annotationsView = annotationsView;
        textCellEditor = new TextCellEditor(treeViewer.getTree());
        checkboxCellEditor = new CheckboxCellEditor(treeViewer.getTree());
        comboBoxCellEditor = new ComboBoxCellEditor(treeViewer.getTree(), new String[] {});
        classDialogCellEditor = new ClassDialogCellEditor(treeViewer.getTree());
        annotationArrayCellEditor = new AnnotationArrayCellEditor(treeViewer.getTree(), new Object[] {});
    }

    @Override
    protected boolean canEdit(Object element) {
        if (element instanceof Method) {
            Method method = (Method)element;
            return (Boolean) getValue(method.getDeclaringClass());
        }
        return true;
    }

    @Override
    protected CellEditor getCellEditor(Object element) {
        if (element instanceof Class) {
            return checkboxCellEditor;
        }
        if (element instanceof Method) {
            Method method = (Method) element;
            final Class<?> returnType = method.getReturnType();
            if (returnType.isEnum()) {
                Object[] enumConstants = returnType.getEnumConstants();
                String[] values = new String[enumConstants.length];
                for (int i = 0; i < enumConstants.length; i++) {
                    values[i] = enumConstants[i].toString();
                }
                comboBoxCellEditor.setItems(values);
                return comboBoxCellEditor;
            }
            if (returnType.equals(Boolean.TYPE)) {
                return checkboxCellEditor;
            }
            
            if (returnType.equals(Class.class)) {
                return classDialogCellEditor;
            }
            
            if (returnType.isArray()) {
                annotationArrayCellEditor.setMethod(method);
                return annotationArrayCellEditor;
            }
            if (returnType.isPrimitive()) {
                textCellEditor.setValidator(new ICellEditorValidator() {
                    public String isValid(Object value) {
                        try {
                            if (returnType.equals(Byte.TYPE)) {
                                Byte.parseByte((String) value);
                            }
                            if (returnType.equals(Short.TYPE)) {
                                Short.parseShort((String) value);
                            }
                            if (returnType.equals(Integer.TYPE)) {
                                Integer.parseInt((String) value);
                            }
                            if (returnType.equals(Long.TYPE)) {
                                Long.parseLong((String) value);
                            }
                            if (returnType.equals(Float.TYPE)) {
                                Float.parseFloat((String) value);
                            }
                            if (returnType.equals(Double.TYPE)) {
                                Double.parseDouble((String) value);
                            }
                        } catch (NumberFormatException nfe) {
                            return JAXWSUIMessages.ANNOTATION_EDITING_SUPPORT_NOT_VALID_MESSAGE_PREFIX 
                                + returnType.getSimpleName();
                        }
                        return null;
                    }
                });
                return textCellEditor;
            }
            return textCellEditor;
        }
        return checkboxCellEditor;
    }
    
    @Override
    protected Object getValue(Object element) {
        if (element instanceof Class) {
            return getValueForClass((Class<?>) element);
        }
        if (element instanceof Method) {
            return getValueForMethod((Method) element);
        }
        return null;
    }
    
    private Object getValueForClass(Class<?> aClass) {
        if (treeViewer.getInput() instanceof IAnnotatable) {
            return getValueForClass(aClass, (IAnnotatable) treeViewer.getInput());
        }
        if (treeViewer.getInput() instanceof SingleVariableDeclaration) {
            return getValueForClass(aClass, (SingleVariableDeclaration) treeViewer.getInput());
        }
        return Boolean.FALSE;
    }
    
    private Object getValueForClass(Class<?> aClass, IAnnotatable annotatedElement) {
        try {
            IAnnotation[] annotations = annotatedElement.getAnnotations();
            for (IAnnotation annotation : annotations) {
                String annotationName = annotation.getElementName();
                if (AnnotationUtils.isAnnotationPresent((IJavaElement)annotatedElement, annotationName)
                        && (annotationName.equals(aClass.getSimpleName())
                        || annotationName.equals(aClass.getCanonicalName()))) {
                    return Boolean.TRUE;
                }
            }
        } catch (JavaModelException jme) {
            JAXWSUIPlugin.log(jme.getStatus());
        } 
        return Boolean.FALSE;
    }
    
    @SuppressWarnings("unchecked")
    private Object getValueForClass(Class<?> aClass, SingleVariableDeclaration parameter) {
        List<IExtendedModifier> modifiers = parameter.modifiers();
        for (IExtendedModifier extendedModifier : modifiers) {
            if (extendedModifier instanceof Annotation) {
                Annotation annotation = (Annotation) extendedModifier;
                String annotationName = AnnotationUtils.getAnnotationName(annotation);
                if (AnnotationUtils.isAnnotationPresent(parameter, annotation)
                        && (annotationName.equals(aClass.getSimpleName())
                        || annotationName.equals(aClass.getCanonicalName()))) {
                    return Boolean.TRUE;
                }
            }
        }
        return Boolean.FALSE;
    }

    private Object getValueForMethod(Method method) {
        Object value = null;
        try {
            if (treeViewer.getInput() instanceof IAnnotatable) {
                value = getValueForMethod(method, (IAnnotatable) treeViewer.getInput());
            } else if (treeViewer.getInput() instanceof SingleVariableDeclaration) {
                value = getValueForMethod(method, (SingleVariableDeclaration) treeViewer
                        .getInput());
            }
        } catch (JavaModelException jme) {
            JAXWSUIPlugin.log(jme.getStatus());
        }
        return value;
    }
    
    private Object getValueForMethod(Method method, IAnnotatable annotatedElement) throws JavaModelException {
        Class<?> returnType = method.getReturnType();
        IAnnotation[] annotations = annotatedElement.getAnnotations();
        for (IAnnotation annotation : annotations) {
            Class<?> declaringClass = method.getDeclaringClass();
            String annotationName = annotation.getElementName();
            if (annotationName.equals(declaringClass.getSimpleName())
                    || annotationName.equals(declaringClass.getCanonicalName())) {
                IMemberValuePair[] memberValuePairs = annotation.getMemberValuePairs();
                for (IMemberValuePair memberValuePair : memberValuePairs) {
                    if (memberValuePair.getMemberName().equals(method.getName())) {
                        if (returnType.equals(String.class)) {
                            return memberValuePair.getValue();
                        }

                        if (returnType.isEnum()) {
                            String enumValue = memberValuePair.getValue().toString();
                            String literal = enumValue.substring(enumValue.lastIndexOf(".") + 1); //$NON-NLS-1$
                            Object[] enumConstants = method.getReturnType().getEnumConstants();
                            for (int i = 0; i < enumConstants.length; i++) {
                                if (enumConstants[i].toString().equals(literal)) {
                                    return i;
                                }
                            }
                        }

                        if (returnType.equals(Class.class)) {
                            return memberValuePair.getValue();
                        }
                        
                        if (returnType.equals(Boolean.TYPE)) {
                            return memberValuePair.getValue();
                        }

                        if (returnType.isPrimitive()) {
                            return ""; //$NON-NLS-1$
                        }
                        if (returnType.isArray()) {
                            if (memberValuePair.getValueKind() == IMemberValuePair.K_CLASS) {
                                Object[] arrayValues = (Object[])memberValuePair.getValue();
                                for (int i = 0; i < arrayValues.length; i++) {
                                    String value = arrayValues[i].toString();
                                    arrayValues[i] = value + ".class";
                                }
                                return arrayValues;
                            }
                            return memberValuePair.getValue();
                        }
                    }
                }
                return getDefaultValueForMethod(returnType);
            }
        }
        return null;
    }
    
    @SuppressWarnings("unchecked")
    private Object getValueForMethod(Method method, SingleVariableDeclaration parameter) {
        Class<?> returnType = method.getReturnType();
        List<IExtendedModifier> modifiers = parameter.modifiers();
        for (IExtendedModifier extendedModifier : modifiers) {
            if (extendedModifier instanceof NormalAnnotation) {
                NormalAnnotation normalAnnotation = (NormalAnnotation) extendedModifier;
                Class<?> declaringClass = method.getDeclaringClass();
                String annotationName = AnnotationUtils.getAnnotationName(normalAnnotation);
                if (annotationName.equals(declaringClass.getSimpleName())
                        || annotationName.equals(declaringClass.getCanonicalName())) {
                    List<MemberValuePair> memberValuePairs = normalAnnotation.values();
                    for (MemberValuePair memberValuePair : memberValuePairs) {
                        if (memberValuePair.getName().toString().equals(method.getName())) {
                            if (returnType.equals(String.class)) {
                                StringLiteral stringLiteral = (StringLiteral) memberValuePair
                                        .getValue();
                                return stringLiteral.getLiteralValue();
                            }

                            if (returnType.isEnum()) {
                                QualifiedName enumValue = (QualifiedName) memberValuePair
                                        .getValue();
                                SimpleName literal = enumValue.getName();
                                
                                Object[] enumConstants = method.getReturnType()
                                        .getEnumConstants();
                                for (int i = 0; i < enumConstants.length; i++) {
                                    if (enumConstants[i].toString().equals(literal.getIdentifier())) {
                                        return i;
                                    }
                                }
                            }

                            if (returnType.equals(Class.class)) {
                                return memberValuePair.getValue();
                            }

                            if (returnType.equals(Boolean.TYPE)) {
                                BooleanLiteral booleanLiteral = (BooleanLiteral) memberValuePair
                                        .getValue();
                                return booleanLiteral.booleanValue();
                            }
                        }
                    }
                    return getDefaultValueForMethod(returnType);
                }
            }
        }
        return null;
    }
    
    private Object getDefaultValueForMethod(Class<?> returnType) {
        if (returnType.equals(String.class)) {
            return ""; //$NON-NLS-1$
        }
        if (returnType.equals(Boolean.TYPE)) {
            return Boolean.FALSE;
        }
        if (returnType.isEnum()) {
            return -1;
        }
        if (returnType.isPrimitive()) {
            return ""; //$NON-NLS-1$
        }
        if (returnType.isArray()) {
            return new Object[] {};
        }
        return null;
    }
        
    @Override
    protected void setValue(Object element, Object value) {
        if (value == null) {
            return;
        }

        try {
            if (element instanceof Class) {
                Class<? extends java.lang.annotation.Annotation> annotationClass = 
                    AnnotationsManager.getAnnotationDefinitionForClass(element).getAnnotationClass();
                
                if (annotationClass != null) {
                    setValueForClass(annotationClass, (Boolean) value);
                }
            }
            if (element instanceof Method) {
                setValueForMethod((Method) element, value);
            }
        } catch (CoreException ce) {
            JAXWSUIPlugin.log(ce.getStatus());
        } 
    }
    
    private void setValueForClass(Class<? extends java.lang.annotation.Annotation> annotationClass, 
            Boolean annotate) throws CoreException {
        Object viewerInput = treeViewer.getInput();

        IAnnotationAttributeInitializer annotationAttributeInitializer = 
            AnnotationsManager.getAnnotationDefinitionForClass(annotationClass).getAnnotationAttributeInitializer();
        
        if (viewerInput instanceof IPackageDeclaration) {
            setValueForClass(annotationClass, annotate, (IPackageDeclaration) viewerInput, 
                    annotationAttributeInitializer);
        } else if (viewerInput instanceof IMember) {
            setValueForClass(annotationClass, annotate, (IMember) viewerInput, annotationAttributeInitializer);
        } else if (viewerInput instanceof SingleVariableDeclaration) {
            setValueForClass(annotationClass, annotate, (SingleVariableDeclaration) viewerInput,
                    annotationAttributeInitializer);
        }
    }
    
    private void setValueForClass(Class<? extends java.lang.annotation.Annotation> annotationClass,
            Boolean annotate, IPackageDeclaration packageDeclaration,
            IAnnotationAttributeInitializer annotationAttributeInitializer) throws CoreException {
        
        ICompilationUnit source = JDTUtils.getCompilationUnitFromFile((IFile)packageDeclaration.getResource());
        CompilationUnit compilationUnit = JDTUtils.getCompilationUnit(source);
        
        PackageDeclaration pkgDeclaration = compilationUnit.getPackage();

        AST ast = pkgDeclaration.getAST();
        ASTRewrite rewriter = ASTRewrite.create(ast);

        List<MemberValuePair> memberValueParis = getMemberValuePairs(annotationAttributeInitializer, 
                pkgDeclaration, ast, annotationClass);

        Annotation annotation = AnnotationsCore.createAnnotation(ast, annotationClass, 
                annotationClass.getSimpleName(), memberValueParis);

        TextFileChange textFileChange = AnnotationUtils.createTextFileChange("AC", (IFile) source.getResource());

        if (annotate) {
            AnnotationUtils.createPackageDeclarationAnnotationChange(source, pkgDeclaration, rewriter,
                    annotation, textFileChange);
        } else {
            AnnotationUtils.removeAnnotationFromPackageDeclaration(source, pkgDeclaration, rewriter, 
                    annotation, textFileChange);
        }

        AnnotationUtils.addImportChange(compilationUnit, annotationClass, textFileChange, annotate);

        executeChange(new NullProgressMonitor(), textFileChange);
    }

    private void setValueForClass(Class<? extends java.lang.annotation.Annotation> annotationClass,
            Boolean annotate, IMember member, IAnnotationAttributeInitializer annotationAttributeInitializer) 
                throws CoreException {
        ICompilationUnit source = member.getCompilationUnit();
        CompilationUnit compilationUnit = JDTUtils.getCompilationUnit(source);
        AST ast = compilationUnit.getAST();
        ASTRewrite rewriter = ASTRewrite.create(ast);

        List<MemberValuePair> memberValueParis = getMemberValuePairs(annotationAttributeInitializer, member,
                ast, annotationClass);

        Annotation annotation = AnnotationsCore.createAnnotation(ast, annotationClass,
                annotationClass.getSimpleName(), memberValueParis);

        TextFileChange textFileChange = AnnotationUtils.createTextFileChange("AC", (IFile) source.getResource());

        if (annotate) {
            if (member.getElementType() == IJavaElement.TYPE) {
                AnnotationUtils.createTypeAnnotationChange(source, compilationUnit, rewriter, 
                        source.findPrimaryType(), annotation, textFileChange);
            } else if (member.getElementType() == IJavaElement.METHOD) {
                AnnotationUtils.createMethodAnnotationChange(source, compilationUnit, rewriter,
                        (IMethod) member, annotation, textFileChange);
            } else if (member.getElementType() == IJavaElement.FIELD) {
                AnnotationUtils.createFieldAnnotationChange(source, compilationUnit, rewriter,
                        (IField) member, annotation, textFileChange);
            }
        } else {
            if (member.getElementType() == IJavaElement.PACKAGE_DECLARATION) {
                
            }
            if (member.getElementType() == IJavaElement.TYPE) {
                AnnotationUtils.removeAnnotationFromType(source, compilationUnit, rewriter,
                        source.findPrimaryType(), annotation, textFileChange);
            } else if (member.getElementType() == IJavaElement.METHOD) {
                AnnotationUtils.removeAnnotationFromMethod(source, compilationUnit, rewriter,
                        (IMethod) member, annotation, textFileChange);
            } else if (member.getElementType() == IJavaElement.FIELD) {
                AnnotationUtils.removeAnnotationFromField(source, compilationUnit, rewriter,
                        (IField) member, annotation, textFileChange);
            }
        }
        
        AnnotationUtils.addImportChange(compilationUnit, annotationClass, textFileChange, annotate);

        executeChange(new NullProgressMonitor(), textFileChange);
    }
  
    private void setValueForClass(Class<? extends java.lang.annotation.Annotation> annotationClass,
            Boolean annotate, SingleVariableDeclaration parameter, 
            IAnnotationAttributeInitializer annotationAttributeInitializer) throws CoreException {
        ITextEditor txtEditor = (ITextEditor) PlatformUI.getWorkbench().getActiveWorkbenchWindow()
                .getActivePage().getActiveEditor();
        IFile file = ((IFileEditorInput) txtEditor.getEditorInput()).getFile();
        ICompilationUnit source = JDTUtils.getCompilationUnitFromFile(file);

        CompilationUnit compilationUnit = JDTUtils.getCompilationUnit(source);
        AST ast = parameter.getAST();
        ASTRewrite rewriter = ASTRewrite.create(ast);

        List<MemberValuePair> memberValueParis = getMemberValuePairs(annotationAttributeInitializer, 
                parameter, ast, annotationClass);

        Annotation annotation = AnnotationsCore.createAnnotation(ast, annotationClass,
                annotationClass.getSimpleName(), memberValueParis);

        TextFileChange textFileChange = AnnotationUtils.createTextFileChange("AC", (IFile) source.getResource());

        if (annotate) {
            AnnotationUtils.createMethodParameterAnnotationChange(source, rewriter, parameter, annotation,
                    textFileChange);
        } else {
            AnnotationUtils.removeAnnotationFromMethodParameter(source, rewriter, parameter, annotation,
                    textFileChange);
        }
        AnnotationUtils.addImportChange(compilationUnit, annotationClass, textFileChange, annotate);

        executeChange(new NullProgressMonitor(), textFileChange);
    }
    
    private List<MemberValuePair> getMemberValuePairs(
            IAnnotationAttributeInitializer annotationAttributeInitializer, ASTNode astNode, AST ast, 
            Class<?extends java.lang.annotation.Annotation> annotationClass) {
        if (annotationAttributeInitializer != null) {
            return annotationAttributeInitializer.getMemberValuePairs(astNode, ast, annotationClass);
        }
        return Collections.emptyList();
    }
    
    private List<MemberValuePair> getMemberValuePairs(
            IAnnotationAttributeInitializer annotationAttributeInitializer, IJavaElement javaElement, AST ast, 
            Class<?extends java.lang.annotation.Annotation> annotationClass) {
        if (annotationAttributeInitializer != null) {
            return annotationAttributeInitializer.getMemberValuePairs(javaElement, ast, annotationClass);
        }
        return Collections.emptyList();
    }


    private void setValueForMethod(Method method, Object value) throws CoreException {
        if (((Boolean) getValue(method.getDeclaringClass())).booleanValue()) {
            Object viewerInput = treeViewer.getInput();
            if (viewerInput instanceof IAnnotatable) {
                setValueForMethod(method, value, (IJavaElement) viewerInput);
            } else if (treeViewer.getInput() instanceof SingleVariableDeclaration) {
                setValueForMethod(method, value, (SingleVariableDeclaration) treeViewer.getInput());
            }
        }
    }
    
    private ICompilationUnit getCompilationUnitForType(IJavaElement javaElement) throws JavaModelException {
        int elementType = javaElement.getElementType();
        if (elementType == IJavaElement.TYPE) {
            IType type = (IType)javaElement.getPrimaryElement();
            return type.getCompilationUnit();
        }
        if (elementType == IJavaElement.METHOD) {
            IMethod method = (IMethod)javaElement.getPrimaryElement();
            return method.getCompilationUnit();
        }
        if (elementType == IJavaElement.FIELD) {
            IField field = (IField)javaElement.getPrimaryElement();
            return field.getCompilationUnit();
        }
        return JDTUtils.getCompilationUnitFromFile((IFile)javaElement.getCorrespondingResource());
    }

    private void setValueForMethod(Method method, Object value, IJavaElement javaElement) throws CoreException {
        ICompilationUnit source = getCompilationUnitForType(javaElement);        
        CompilationUnit compilationUnit = JDTUtils.getCompilationUnit(source);
        AST ast = compilationUnit.getAST();
        ASTRewrite rewriter = ASTRewrite.create(ast);

        TextFileChange textFileChange = AnnotationUtils.createTextFileChange("AC", (IFile) source.getResource());

        IAnnotatable annotatedElement = (IAnnotatable) javaElement;
        IAnnotation[] annotations = annotatedElement.getAnnotations();
        for (IAnnotation annotation : annotations) {
            Class<?> declaringClass = method.getDeclaringClass();
            String annotationName = annotation.getElementName();
            if (annotationName.equals(declaringClass.getSimpleName())
                    || annotationName.equals(declaringClass.getCanonicalName())) {
                IMemberValuePair[] memberValuePairs = annotation.getMemberValuePairs();
                boolean hasMemberValuePair = false;
                for (IMemberValuePair memberValuePair : memberValuePairs) {
                    if (memberValuePair.getMemberName().equals(method.getName())) {
                        ASTNode memberValue = getMemberValuePairValue(ast, method, value);
                        if (memberValue != null) {
                            AnnotationUtils.updateMemberValuePairValue(source,
                                    compilationUnit, rewriter, javaElement, annotation,
                                    memberValuePair, memberValue, textFileChange);
                            hasMemberValuePair = true;
                            break;
                        }
                    }
                }
                if (!hasMemberValuePair) {
                    ASTNode memberValuePair = getMemberValuePair(ast, method, value);
                    if (memberValuePair != null) {
                        AnnotationUtils
                                .createMemberValuePairChange(source, compilationUnit,
                                        rewriter, javaElement, annotation, memberValuePair,
                                        textFileChange);
                        break;
                    }
                }
            }
        }
        executeChange(new NullProgressMonitor(), textFileChange);
    }
    
    @SuppressWarnings("unchecked")
    private void setValueForMethod(Method method, Object value, SingleVariableDeclaration parameter) 
            throws CoreException {
        ITextEditor txtEditor = (ITextEditor) PlatformUI.getWorkbench().getActiveWorkbenchWindow()
                .getActivePage().getActiveEditor();
        IFile file = ((IFileEditorInput) txtEditor.getEditorInput()).getFile();
        ICompilationUnit source = JDTUtils.getCompilationUnitFromFile(file);

        CompilationUnit compilationUnit = JDTUtils.getCompilationUnit(source);
        AST ast = parameter.getAST();
        ASTRewrite rewriter = ASTRewrite.create(ast);

        TextFileChange textFileChange = AnnotationUtils.createTextFileChange("AC", (IFile) source.getResource());

        List<IExtendedModifier> modifiers = parameter.modifiers();
        for (IExtendedModifier extendedModifier : modifiers) {
            if (extendedModifier instanceof NormalAnnotation) {
                NormalAnnotation normalAnnotation = (NormalAnnotation) extendedModifier;
                String annotationName = AnnotationUtils.getAnnotationName(normalAnnotation);
                Class<?> declaringClass = method.getDeclaringClass();
                if (annotationName.equals(declaringClass.getSimpleName())
                        || annotationName.equals(declaringClass.getCanonicalName())) {
                    List<MemberValuePair> memberValuePairs = normalAnnotation.values();
                    boolean hasMemberValuePair = false;
                    for (MemberValuePair memberValuePair : memberValuePairs) {
                        if (memberValuePair.getName().toString().equals(method.getName())) {
                            ASTNode memberValue = getMemberValuePairValue(ast, method, value);
                            if (memberValue != null) {
                                AnnotationUtils.updateMemberValuePairValue(source, compilationUnit, rewriter,
                                        normalAnnotation, memberValuePair, memberValue, textFileChange);
                                hasMemberValuePair = true;
                                break;
                            }
                        }
                    }
                    if (!hasMemberValuePair) {
                        ASTNode memberValuePair = getMemberValuePair(ast, method, value);
                        if (memberValuePair != null) {
                            AnnotationUtils.createMemberValuePairChange(source, compilationUnit, rewriter,
                                    normalAnnotation, memberValuePair, textFileChange);
                            break;
                        }
                    }
                }
            }
        }
        executeChange(new NullProgressMonitor(), textFileChange);
    }

    private ASTNode getMemberValuePairValue(AST ast, Method method, Object value) {
        Class<?> returnType = method.getReturnType();
        if (returnType.equals(String.class)) {
            return AnnotationsCore.createStringLiteral(ast, value.toString());
        }
        if (returnType.equals(Boolean.TYPE)) {
            return AnnotationsCore.createBooleanLiteral(ast, ((Boolean) value).booleanValue());
        }
        if (returnType.isPrimitive()
                && (returnType.equals(Byte.TYPE) || returnType.equals(Short.TYPE)
                        || returnType.equals(Integer.TYPE) || returnType.equals(Long.TYPE)
                        || returnType.equals(Float.TYPE) || returnType.equals(Double.TYPE))) {
            return AnnotationsCore.createNumberLiteral(ast, value.toString());
        }
        if (returnType.isArray()) {
            return AnnotationsCore.createArrayValueLiteral(ast, method, (Object[]) value);
        }
        
        if (returnType.equals(Class.class)) {
            return AnnotationsCore.createTypeLiteral(ast, value.toString());
        }
        
        if (returnType.isEnum()) {
            int selected = ((Integer) value).intValue();
            if (selected != -1) {
                return AnnotationsCore.createEnumLiteral(ast, method.getDeclaringClass().getCanonicalName(),
                        method.getReturnType().getEnumConstants()[selected]);
            }
        }
        return null;
    }

    private ASTNode getMemberValuePair(AST ast, Method method, Object value) {
        Class<?> returnType = method.getReturnType();
        if (returnType.equals(String.class)) {
            return AnnotationsCore.createStringMemberValuePair(ast, method.getName(), value);
        }
        if (returnType.equals(Boolean.TYPE)) {
            return AnnotationsCore.createBooleanMemberValuePair(ast, method.getName(), value);
        }
        if (returnType.isPrimitive()
                && (returnType.equals(Byte.TYPE) || returnType.equals(Short.TYPE)
                        || returnType.equals(Integer.TYPE) || returnType.equals(Long.TYPE)
                        || returnType.equals(Float.TYPE) || returnType.equals(Double.TYPE))) {
            return AnnotationsCore.createNumberMemberValuePair(ast, method.getName(), value.toString());
        }
        if (returnType.isArray()) {
            return AnnotationsCore.createArrayMemberValuePair(ast, method, (Object[]) value);
        }
        
        if (returnType.equals(Class.class)) {
            return AnnotationsCore.createTypeMemberValuePair(ast, method.getName(), value.toString());
        }

        if (returnType.isEnum()) {
            int selected = ((Integer) value).intValue();
            if (selected != -1) {
                return AnnotationsCore.createEnumMemberValuePair(ast, 
                       method.getDeclaringClass().getCanonicalName(), method.getName(), method.getReturnType()
                        .getEnumConstants()[selected]);
            }
        }
        return null;
    }

    private void executeChange(IProgressMonitor monitor, Change change) {
        if (change == null) {
            return;
        }

        IUndoManager manager= RefactoringCore.getUndoManager();
        boolean successful = false;
        Change undoChange = null;
        try {
            change.initializeValidationData(monitor);
            RefactoringStatus valid = change.isValid(monitor);
            if (valid.isOK()) {
                manager.aboutToPerformChange(change);
                undoChange = change.perform(monitor);
                successful = true;
            }
        } catch (CoreException ce) {
            ce.printStackTrace();
        } finally {
            manager.changePerformed(change, successful);
        }
        if (undoChange != null) {
            undoChange.initializeValidationData(monitor);
            manager.addUndo(undoChange.getName(), undoChange);
        }
        annotationsView.refresh();
    }
}