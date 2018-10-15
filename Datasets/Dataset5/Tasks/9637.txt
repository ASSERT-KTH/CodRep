annotationsView.refreshLabels();

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
import org.eclipse.jdt.core.IJavaElement;
import org.eclipse.jdt.core.IMemberValuePair;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.Expression;
import org.eclipse.jdt.core.dom.MemberValuePair;
import org.eclipse.jdt.core.dom.NormalAnnotation;
import org.eclipse.jdt.core.dom.SingleMemberAnnotation;
import org.eclipse.jdt.ui.SharedASTProvider;
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
import org.eclipse.ltk.core.refactoring.Change;
import org.eclipse.ltk.core.refactoring.IUndoManager;
import org.eclipse.ltk.core.refactoring.RefactoringCore;
import org.eclipse.ltk.core.refactoring.RefactoringStatus;
import org.eclipse.ltk.core.refactoring.TextFileChange;
import org.eclipse.text.edits.MultiTextEdit;

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

    private Object getValueForMethod(Method method) {
        Object value = null;
        try {
            if (treeViewer.getInput() instanceof IAnnotatable) {
                value = getValueForMethod(method, (IAnnotatable) treeViewer.getInput());
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
                                    arrayValues[i] = value + ".class"; //$NON-NLS-1$
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
            if (element instanceof Class && ((Class<?>) element).isAnnotation()) {
                @SuppressWarnings("unchecked")
                Class<? extends java.lang.annotation.Annotation> annotationClass =
                    		(Class<? extends java.lang.annotation.Annotation>) element;
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

        if (viewerInput instanceof IJavaElement) {
            setValueForClass(annotationClass, annotate, (IJavaElement) viewerInput, annotationAttributeInitializer);
        }
    }

    private Annotation getAnnotation(AST ast, Class<? extends java.lang.annotation.Annotation> annotationClass,
            List<MemberValuePair> memberValuePairs) {

        Annotation annotation =  null;
        int numberOfDeclaredMethods = annotationClass.getDeclaredMethods().length;
        if (numberOfDeclaredMethods == 0) {
            annotation = AnnotationsCore.createMarkerAnnotation(ast, annotationClass.getSimpleName());
        } else if (numberOfDeclaredMethods == 1) {
            Expression value = null;
            if (memberValuePairs != null && memberValuePairs.size() == 1) {
                MemberValuePair memberValuePair = memberValuePairs.get(0);
                if (memberValuePair != null) {
                    value = memberValuePair.getValue();
                }
            }
            if (value != null) {
                annotation = AnnotationsCore.createSingleMemberAnnotation(ast, annotationClass.getSimpleName(), value);
            } else {
                annotation = AnnotationsCore.createNormalAnnotation(ast, annotationClass.getSimpleName(), memberValuePairs);
            }
        } else if (numberOfDeclaredMethods > 1) {
            annotation = AnnotationsCore.createNormalAnnotation(ast, annotationClass.getSimpleName(), memberValuePairs);
        }

        return annotation;
    }

    private void setValueForClass(Class<? extends java.lang.annotation.Annotation> annotationClass,
            Boolean annotate, IJavaElement javaElement, IAnnotationAttributeInitializer annotationAttributeInitializer)
                throws CoreException {
        ICompilationUnit source = AnnotationUtils.getCompilationUnitFromJavaElement(javaElement);
        CompilationUnit compilationUnit = SharedASTProvider.getAST(source, SharedASTProvider.WAIT_YES, null);
        AST ast = compilationUnit.getAST();

        List<MemberValuePair> memberValuePairs = getMemberValuePairs(annotationAttributeInitializer, javaElement,
                ast, annotationClass);

        Annotation annotation = getAnnotation(ast, annotationClass, memberValuePairs);

        TextFileChange change = new TextFileChange("Add/Remove Annotation", (IFile) source.getResource()); //$NON-NLS-1$
        MultiTextEdit multiTextEdit = new MultiTextEdit();
        change.setEdit(multiTextEdit);

        if (annotate) {
            if (javaElement.getElementType() == IJavaElement.PACKAGE_DECLARATION
                    || javaElement.getElementType() == IJavaElement.TYPE
                    || javaElement.getElementType() == IJavaElement.FIELD
                    || javaElement.getElementType() == IJavaElement.METHOD
                    || javaElement.getElementType() == IJavaElement.LOCAL_VARIABLE) {
                change.addEdit(AnnotationUtils.createAddAnnotationTextEdit(javaElement, annotation));
                change.addEdit(AnnotationUtils.createAddImportTextEdit(javaElement, annotationClass.getCanonicalName()));
            }
        } else {
            if (javaElement.getElementType() == IJavaElement.PACKAGE_DECLARATION
                    || javaElement.getElementType() == IJavaElement.TYPE
                    || javaElement.getElementType() == IJavaElement.FIELD
                    || javaElement.getElementType() == IJavaElement.METHOD
                    || javaElement.getElementType() == IJavaElement.LOCAL_VARIABLE) {
                change.addEdit(AnnotationUtils.createRemoveAnnotationTextEdit(javaElement, annotation));
                change.addEdit(AnnotationUtils.createRemoveImportTextEdit(javaElement, annotationClass.getCanonicalName()));
            }
        }
        executeChange(new NullProgressMonitor(), change);
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
            }
        }
    }

    private void setValueForMethod(Method method, Object value, IJavaElement javaElement) throws CoreException {
        ICompilationUnit source = AnnotationUtils.getCompilationUnitFromJavaElement(javaElement);
        CompilationUnit compilationUnit = SharedASTProvider.getAST(source, SharedASTProvider.WAIT_YES, null);
        AST ast = compilationUnit.getAST();

        TextFileChange change = new TextFileChange("Add/Update Annotation Value", (IFile) source.getResource());
        MultiTextEdit multiTextEdit = new MultiTextEdit();
        change.setEdit(multiTextEdit);

        List<Annotation> annotations = AnnotationUtils.getAnnotations(javaElement);
        for (Annotation annotation : annotations) {
            if (annotation instanceof NormalAnnotation) {
                NormalAnnotation normalAnnotation = (NormalAnnotation) annotation;
                Class<?> declaringClass = method.getDeclaringClass();
                String annotationName = normalAnnotation.getTypeName().getFullyQualifiedName();
                if (annotationName.equals(declaringClass.getSimpleName()) || annotationName.equals(declaringClass.getCanonicalName())) {
                    @SuppressWarnings("unchecked")
                    List<MemberValuePair> memberValuePairs = normalAnnotation.values();
                    boolean hasMemberValuePair = false;
                    for (MemberValuePair memberValuePair : memberValuePairs) {
                        if (memberValuePair.getName().getIdentifier().equals(method.getName())) {
                            ASTNode memberValue = getMemberValuePairValue(ast, method, value);
                            if (memberValue != null) {
                                change.addEdit(AnnotationUtils.createUpdateMemberValuePairTextEdit(memberValuePair, memberValue));
                                hasMemberValuePair = true;
                                break;
                            }
                        }
                    }
                    if (!hasMemberValuePair) {
                        MemberValuePair memberValuePair = getMemberValuePair(ast, method, value);
                        if (memberValuePair != null) {
                            change.addEdit(AnnotationUtils.createAddMemberValuePairTextEdit(normalAnnotation, memberValuePair));
                            break;
                        }
                    }
                }
            } else if (annotation instanceof SingleMemberAnnotation) {
                SingleMemberAnnotation singleMemberAnnotation = (SingleMemberAnnotation) annotation;
                Class<?> declaringClass = method.getDeclaringClass();
                String annotationName = singleMemberAnnotation.getTypeName().getFullyQualifiedName();
                if (annotationName.equals(declaringClass.getSimpleName()) || annotationName.equals(declaringClass.getCanonicalName())) {
                    MemberValuePair memberValuePair = getMemberValuePair(ast, method, value);
                    if (memberValuePair != null) {
                        change.addEdit(AnnotationUtils.createUpdateSingleMemberAnnotationTextEdit(singleMemberAnnotation, memberValuePair.getValue()));
                        break;
                    }
                }

            }
        }

        executeChange(new NullProgressMonitor(), change);
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

    private MemberValuePair getMemberValuePair(AST ast, Method method, Object value) {
        Class<?> returnType = method.getReturnType();
        if (returnType.equals(String.class)) {
            return AnnotationsCore.createStringMemberValuePair(ast, method.getName(), (String) value);
        }
        if (returnType.equals(Boolean.TYPE)) {
            return AnnotationsCore.createBooleanMemberValuePair(ast, method.getName(), (Boolean) value);
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

        IUndoManager manager = RefactoringCore.getUndoManager();
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
            JAXWSUIPlugin.log(ce.getStatus());
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