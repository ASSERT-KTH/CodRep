if (JDTUtils.isPublicMethod(method)) {

/*******************************************************************************
 * Copyright (c) 2008 IONA Technologies PLC
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 * IONA Technologies PLC - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.internal.cxf.core.utils;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.Map.Entry;

import javax.jws.WebMethod;
import javax.jws.WebParam;
import javax.jws.WebService;
import javax.xml.ws.RequestWrapper;
import javax.xml.ws.ResponseWrapper;

import org.eclipse.core.filebuffers.FileBuffers;
import org.eclipse.core.filebuffers.ITextFileBufferManager;
import org.eclipse.core.filebuffers.LocationKind;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.ICompilationUnit;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jdt.core.dom.BodyDeclaration;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.IExtendedModifier;
import org.eclipse.jdt.core.dom.MemberValuePair;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.Name;
import org.eclipse.jdt.core.dom.QualifiedName;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jdt.core.dom.TypeDeclaration;
import org.eclipse.jdt.core.dom.rewrite.ASTRewrite;
import org.eclipse.jdt.core.dom.rewrite.ImportRewrite;
import org.eclipse.jdt.core.dom.rewrite.ListRewrite;
import org.eclipse.ltk.core.refactoring.TextFileChange;
import org.eclipse.jdt.ui.CodeStyleConfiguration;
import org.eclipse.jface.text.IDocument;
import org.eclipse.jst.ws.internal.cxf.core.CXFCorePlugin;
import org.eclipse.jst.ws.internal.cxf.core.annotations.JAXWSAnnotations;
import org.eclipse.jst.ws.internal.cxf.core.model.Java2WSDataModel;
import org.eclipse.ltk.core.refactoring.TextChange;
import org.eclipse.text.edits.TextEdit;
import org.eclipse.text.edits.TextEditGroup;

/**
 * @author sclarke
 * 
 */
public final class AnnotationUtils {
    public static final String WEB_SERVICE = "WebService"; //$NON-NLS-1$
    public static final String WEB_METHOD = "WebMethod"; //$NON-NLS-1$
    public static final String WEB_PARAM = "WebParam"; //$NON-NLS-1$
    public static final String REQUEST_WRAPPER = "RequestWrapper"; //$NON-NLS-1$
    public static final String RESPONSE_WRAPPER = "ResponseWrapper"; //$NON-NLS-1$

    private static Map<String, String> ANNOTATION_TYPENAME_MAP = new HashMap<String, String>();

    static {
        ANNOTATION_TYPENAME_MAP.put("ServiceMode", "javax.xml.ws.ServiceMode"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put("WebFault", "javax.xml.ws.WebFault"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put(REQUEST_WRAPPER, "javax.xml.ws.RequestWrapper"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put(RESPONSE_WRAPPER, "javax.xml.ws.ResponseWrapper"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put("WebServiceClient", "javax.xml.ws.WebServiceClient"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put("WebEndpoint", "javax.xml.ws.WebEndpoint"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put("WebServiceProvider", "javax.xml.ws.WebServiceProvider"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put("BindingType", "javax.xml.ws.BindingType"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put("WebServiceRef", "javax.xml.ws.WebServiceRef"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put("WebServiceRefs", "javax.xml.ws.WebServiceRefs"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put(WEB_SERVICE, "javax.jws.WebService"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put(WEB_METHOD, "javax.jws.WebMethod"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put("Oneway", "javax.jws.OneWay"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put(WEB_PARAM, "javax.jws.WebParam"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put("WebResult", "javax.jws.WebResult"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put("SOAPBinding", "javax.jws.SOAPBinding"); //$NON-NLS-1$ //$NON-NLS-2$
        ANNOTATION_TYPENAME_MAP.put("HandlerChain", "javax.jws.HandlerChain"); //$NON-NLS-1$ //$NON-NLS-2$
    }

    private AnnotationUtils() {
    }
    
    public static TextChange getWebServiceAnnotationChange(IType type, Java2WSDataModel model, 
    		TextFileChange textFileChange) throws CoreException {
        ICompilationUnit source = type.getCompilationUnit();

        CompilationUnit compilationUnit = getASTParser(source);

        AST ast = compilationUnit.getAST();
        ASTRewrite rewriter = ASTRewrite.create(ast);
        
        String typeName = type.getElementName();
        String packageName = type.getPackageFragment().getElementName();

        List<MemberValuePair> memberValuePairs = new ArrayList<MemberValuePair>();

        MemberValuePair nameValuePair = JAXWSAnnotations.getNameValuePair(compilationUnit, typeName);

        MemberValuePair targetNamespaceValuePair = JAXWSAnnotations.getTargetNamespaceValuePair(
                compilationUnit, model.getTargetNamespace());

        MemberValuePair portNameValuePair = JAXWSAnnotations.getPortNameValuePair(compilationUnit, typeName
                + "Port"); //$NON-NLS-1$

        MemberValuePair serviceNameValuePair = JAXWSAnnotations.getServiceNameValuePair(compilationUnit,
                typeName + "Service"); //$NON-NLS-1$

        if (model.isUseServiceEndpointInterface()) {
            try {
                if (type.isInterface()) {
                    memberValuePairs.add(nameValuePair);
                    memberValuePairs.add(targetNamespaceValuePair);
                } else if (type.isClass()) {
                    MemberValuePair endpointInterfaceValuePair = JAXWSAnnotations
                            .getEndpointInterfaceValuePair(compilationUnit, model
                                    .getFullyQualifiedJavaInterfaceName());
                    memberValuePairs.add(endpointInterfaceValuePair);
                    memberValuePairs.add(portNameValuePair);
                    memberValuePairs.add(serviceNameValuePair);
                    
                    if  (packageName == null || packageName.length() == 0) {
                        memberValuePairs.add(targetNamespaceValuePair);
                    }
                    
                }
            } catch (JavaModelException jme) {
                CXFCorePlugin.log(jme.getStatus());
            }
        } else {
            memberValuePairs.add(nameValuePair);
            memberValuePairs.add(targetNamespaceValuePair);
            memberValuePairs.add(portNameValuePair);
            memberValuePairs.add(serviceNameValuePair);
        }

        Annotation annotation = JAXWSAnnotations.getAnnotation(ast, WebService.class, memberValuePairs);
        return AnnotationUtils.createTypeAnnotationChange(source, compilationUnit, rewriter, annotation, 
        		textFileChange);
    }

    public static TextChange getWebMethodAnnotationChange(IType type, IMethod method, 
    		TextFileChange textFileChange) throws CoreException {
        ICompilationUnit source = type.getCompilationUnit();
        CompilationUnit compilationUnit = getASTParser(source);

        AST ast = compilationUnit.getAST();
        ASTRewrite rewriter = ASTRewrite.create(ast);

        List<MemberValuePair> memberValuePairs = new ArrayList<MemberValuePair>();

        MemberValuePair operationValuePair = JAXWSAnnotations.getOperationNameValuePair(compilationUnit,
                method.getElementName());

        memberValuePairs.add(operationValuePair);

        Annotation annotation = JAXWSAnnotations.getAnnotation(ast, WebMethod.class, memberValuePairs);

        return AnnotationUtils.createMethodAnnotationChange(source, compilationUnit, rewriter, method,
                annotation, textFileChange);
    }

    @SuppressWarnings("unchecked")
    public static List<SingleVariableDeclaration> getMethodParameters(IType type, final IMethod method) {
        ICompilationUnit source = type.getCompilationUnit();
        CompilationUnit compilationUnit = getASTParser(source);
        final List<SingleVariableDeclaration> parameters = new ArrayList();
        compilationUnit.accept(new ASTVisitor() {
            @Override
            public boolean visit(MethodDeclaration methodDeclaration) {
                if (methodDeclaration.getName().getIdentifier().equals(method.getElementName())) {
                    parameters.addAll(methodDeclaration.parameters());
                }
                return super.visit(methodDeclaration);
            }
        });
        
        return parameters;
    }
    
    public static TextChange getWebParamAnnotationChange(IType type, final IMethod method, 
            SingleVariableDeclaration parameter, TextFileChange textFileChange) 
            throws CoreException {
        ICompilationUnit source = type.getCompilationUnit();
        CompilationUnit compilationUnit = getASTParser(source);

        AST ast = compilationUnit.getAST();
        ASTRewrite rewriter = ASTRewrite.create(ast);

        List<MemberValuePair> memberValuePairs = new ArrayList<MemberValuePair>();
        MemberValuePair nameValuePair = JAXWSAnnotations.getNameValuePair(compilationUnit,
                parameter.getName().getIdentifier());
        memberValuePairs.add(nameValuePair);
        Annotation annotation = JAXWSAnnotations.getAnnotation(ast, WebParam.class, memberValuePairs);
 
        return AnnotationUtils.createMethodParameterAnnotationChange(source, compilationUnit, 
                rewriter, parameter, method, annotation, textFileChange);
    }

    public static TextChange getRequestWrapperAnnotationChange(IType type, IMethod method, 
    		TextFileChange textFileChange) throws CoreException {
        ICompilationUnit source = type.getCompilationUnit();
        CompilationUnit compilationUnit = getASTParser(source);

        AST ast = compilationUnit.getAST();
        ASTRewrite rewriter = ASTRewrite.create(ast);

        String methodName = method.getElementName();
        String packageName = type.getPackageFragment().getElementName();
        if (packageName == null || packageName.length() == 0) {
            packageName = "default_package"; //$NON-NLS-1$
        }
        packageName += "."; //$NON-NLS-1$

        List<MemberValuePair> memberValuePairs = new ArrayList<MemberValuePair>();

        String className = packageName + methodName.substring(0, 1).toUpperCase(Locale.getDefault())
                + methodName.substring(1);
        MemberValuePair classNameValuePair = JAXWSAnnotations.getClassNameValuePair(compilationUnit,
                className);

        MemberValuePair localNameValuePair = JAXWSAnnotations.getLocalNameValuePair(compilationUnit,
                methodName);

        MemberValuePair targetNamespace = JAXWSAnnotations.getTargetNamespaceValuePair(compilationUnit,
                JDTUtils.getTargetNamespaceFromPackageName(packageName));

        memberValuePairs.add(classNameValuePair);
        memberValuePairs.add(localNameValuePair);
        memberValuePairs.add(targetNamespace);

        Annotation annotation = JAXWSAnnotations.getAnnotation(ast, RequestWrapper.class, memberValuePairs);

        return AnnotationUtils.createMethodAnnotationChange(source, compilationUnit, rewriter, method, 
                annotation, textFileChange);
    }

    public static TextChange getResponseWrapperAnnotationChange(IType type, IMethod method,
    		TextFileChange textFileChange) throws CoreException {
        ICompilationUnit source = type.getCompilationUnit();
        CompilationUnit compilationUnit = getASTParser(source);

        AST ast = compilationUnit.getAST();
        ASTRewrite rewriter = ASTRewrite.create(ast);

        String methodName = method.getElementName() + "Response"; //$NON-NLS-1$
        String packageName = type.getPackageFragment().getElementName();
        if (packageName == null || packageName.length() == 0) {
            packageName = "default_package"; //$NON-NLS-1$
        }
        packageName += "."; //$NON-NLS-1$
        
        List<MemberValuePair> memberValuePairs = new ArrayList<MemberValuePair>();

        String className = packageName + methodName.substring(0, 1).toUpperCase(Locale.getDefault())
                + methodName.substring(1);

        MemberValuePair classNameValuePair = JAXWSAnnotations.getClassNameValuePair(compilationUnit,
                className);

        MemberValuePair localNameValuePair = JAXWSAnnotations.getLocalNameValuePair(compilationUnit,
                methodName);

        MemberValuePair targetNamespace = JAXWSAnnotations.getTargetNamespaceValuePair(compilationUnit,
                JDTUtils.getTargetNamespaceFromPackageName(packageName));

        memberValuePairs.add(classNameValuePair);
        memberValuePairs.add(localNameValuePair);
        memberValuePairs.add(targetNamespace);

        Annotation annotation = JAXWSAnnotations.getAnnotation(ast, ResponseWrapper.class, memberValuePairs);

        return AnnotationUtils.createMethodAnnotationChange(source, compilationUnit, rewriter, method, 
                annotation, textFileChange);
    }

    
    public static void getImportsChange(ICompilationUnit compilationUnit, Java2WSDataModel model, 
    		TextFileChange textFileChange, boolean classOnly) {
        try {
        
            ImportRewrite importRewrite = CodeStyleConfiguration.createImportRewrite(compilationUnit, true);
            
            importRewrite.addImport(ANNOTATION_TYPENAME_MAP.get(WEB_SERVICE));
            
            if (!classOnly) {
                Map<IMethod, Map<String, Boolean>> methodAnnotationMap = model.getMethodMap();
                Set<Entry<IMethod, Map<String, Boolean>>> methodAnnotationSet = methodAnnotationMap.entrySet();
                for (Map.Entry<IMethod, Map<String, Boolean>> methodAnnotation : methodAnnotationSet) {
                    Map<String, Boolean> methodMap = methodAnnotation.getValue();
                    Set<Entry<String, Boolean>> methodSet = methodMap.entrySet();
                    for (Map.Entry<String, Boolean> method : methodSet) {
                        if (ANNOTATION_TYPENAME_MAP.containsKey(method.getKey()) && method.getValue()) {
                            importRewrite.addImport(ANNOTATION_TYPENAME_MAP.get(method.getKey()));
                        }
                    }                    
                }
            }
            if (importRewrite.hasRecordedChanges()) {
                    TextEdit importTextEdit = importRewrite.rewriteImports(null);
                    textFileChange.addEdit(importTextEdit);
            }
        } catch (CoreException ce) {
            CXFCorePlugin.log(ce.getStatus());
        }
    }
    
    @SuppressWarnings("unchecked")
    private static TextChange createTypeAnnotationChange(ICompilationUnit source, CompilationUnit 
            compilationUnit, ASTRewrite rewriter, Annotation annotation, 
            TextFileChange textFileChange) throws CoreException {
        IProgressMonitor monitor = new NullProgressMonitor();
        IPath path = source.getResource().getFullPath();
        ITextFileBufferManager bufferManager = FileBuffers.getTextFileBufferManager();
        try {
            IType type = compilationUnit.getTypeRoot().findPrimaryType();
            List<TypeDeclaration> types = compilationUnit.types();
            for (TypeDeclaration typeDeclaration : types) {
                if (typeDeclaration.getName().getIdentifier().equals(type.getElementName())
                        && !isAnnotationPresent(typeDeclaration, annotation)) {

                    bufferManager.connect(path, LocationKind.IFILE, monitor);
                    IDocument document = bufferManager.getTextFileBuffer(path, 
                            LocationKind.IFILE).getDocument();

                    ListRewrite listRewrite = rewriter.getListRewrite(typeDeclaration,
                            TypeDeclaration.MODIFIERS2_PROPERTY);
                    listRewrite.insertFirst(annotation, null);
                    
                    TextEdit annotationTextEdit = rewriter.rewriteAST(document, source.getJavaProject()
                            .getOptions(true));
                    
                    textFileChange.addEdit(annotationTextEdit);

                    textFileChange.addTextEditGroup(new TextEditGroup("AA", new  //$NON-NLS-1$
                            TextEdit[] {annotationTextEdit}));
                    
                    return textFileChange;
                }
            }
        } catch (CoreException ce) {
            CXFCorePlugin.log(ce.getStatus());
        } finally {
            bufferManager.disconnect(path, LocationKind.IFILE, monitor);
        }
        return null;
    }
    
    @SuppressWarnings("unchecked")
    private static TextChange createMethodAnnotationChange(ICompilationUnit source, CompilationUnit 
            compilationUnit, ASTRewrite rewriter, IMethod method, Annotation annotation, 
            TextFileChange textFileChange) throws CoreException {
        IProgressMonitor monitor = new NullProgressMonitor();
        IPath path = source.getResource().getFullPath();
        ITextFileBufferManager bufferManager = FileBuffers.getTextFileBufferManager();
        try {
            IType type = method.getDeclaringType();
            List<TypeDeclaration> types = compilationUnit.types();
            for (TypeDeclaration typeDeclaration : types) {
                if (typeDeclaration.getName().getIdentifier().equals(type.getElementName())) {
                    String methodToAnnotateName = method.getElementName();
                    MethodDeclaration[] methodDeclarations = typeDeclaration.getMethods();
                    for (int i = 0; i < methodDeclarations.length; i++) {
                        MethodDeclaration methodDeclaration = methodDeclarations[i];
                        if (methodDeclaration.getName().getIdentifier().equals(methodToAnnotateName)
                                && !isAnnotationPresent(methodDeclaration, annotation)) {
                            bufferManager.connect(path, LocationKind.IFILE, monitor);
                            IDocument document = bufferManager.getTextFileBuffer(path, 
                                    LocationKind.IFILE).getDocument();

                            ListRewrite listRewrite = rewriter.getListRewrite(methodDeclaration,
                                    MethodDeclaration.MODIFIERS2_PROPERTY);
                            listRewrite.insertAt(annotation, 0, null);
                            
                            TextEdit annotationTextEdit = rewriter.rewriteAST(document, source
                                    .getJavaProject().getOptions(true));
                            
                            textFileChange.addEdit(annotationTextEdit);
                            textFileChange.addTextEditGroup(new TextEditGroup("AA", new  //$NON-NLS-1$
                                    TextEdit[] {annotationTextEdit}));
                            
                            return textFileChange;
                        }
                    }
                }
            }
        } catch (CoreException ce) {
            CXFCorePlugin.log(ce.getStatus());
        } finally {
            bufferManager.disconnect(path, LocationKind.IFILE, monitor);
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    private static TextChange createMethodParameterAnnotationChange(ICompilationUnit source, CompilationUnit 
            compilationUnit, ASTRewrite rewriter, SingleVariableDeclaration singleVariableDeclaration, 
            IMethod method, Annotation annotation, TextFileChange textFileChange) 
            throws CoreException {
        IProgressMonitor monitor = new NullProgressMonitor();
        IPath path = source.getResource().getFullPath();
        ITextFileBufferManager bufferManager = FileBuffers.getTextFileBufferManager();
        try {
            IType type = method.getDeclaringType();
            List<TypeDeclaration> types = compilationUnit.types();
            for (TypeDeclaration typeDeclaration : types) {
                if (typeDeclaration.getName().getIdentifier().equals(type.getElementName())) {
                    String methodToAnnotateName = method.getElementName();
                    MethodDeclaration[] methodDeclarations = typeDeclaration.getMethods();
                    for (int i = 0; i < methodDeclarations.length; i++) {
                        MethodDeclaration methodDeclaration = methodDeclarations[i];
                        if (methodDeclaration.getName().getIdentifier().equals(methodToAnnotateName)) {
                            List<SingleVariableDeclaration> parameters = methodDeclaration.parameters();
                            for (SingleVariableDeclaration parameter : parameters) {
                                if (compareMethodParameters(parameter, singleVariableDeclaration)
                                        && !isAnnotationPresent(parameter, annotation)) {
                                    bufferManager.connect(path, LocationKind.IFILE, monitor);
                                    IDocument document = bufferManager.getTextFileBuffer(path, 
                                            LocationKind.IFILE).getDocument();
                                    
                                    ListRewrite listRewrite = rewriter.getListRewrite(parameter,
                                            SingleVariableDeclaration.MODIFIERS2_PROPERTY);
                                    
                                    listRewrite.insertAt(annotation, -1, null);

                                    TextEdit annotationTextEdit = rewriter.rewriteAST(document, source
                                            .getJavaProject().getOptions(true));
                                    
                                    textFileChange.addEdit(annotationTextEdit);
                                    
                                    textFileChange.addTextEditGroup(new TextEditGroup("AA", new  //$NON-NLS-1$
                                            TextEdit[] {annotationTextEdit}));
                                    
                                    return textFileChange;
                                }
                            }
                        }
                    }
                }
            }
        } catch (CoreException ce) {
            CXFCorePlugin.log(ce.getStatus());
        } finally {
            bufferManager.disconnect(path, LocationKind.IFILE, monitor);
        }
        
        return null;
    }

    public static CompilationUnit getASTParser(ICompilationUnit source) {
        ASTParser parser = ASTParser.newParser(AST.JLS3);
        parser.setSource(source);

        CompilationUnit compilationUnit = (CompilationUnit) parser.createAST(new NullProgressMonitor());
        compilationUnit.recordModifications();
        return compilationUnit;
    }

    private static String getAnnotationName(Annotation annotation) {
        Name annotationTypeName = annotation.getTypeName();
        String annotationName = annotationTypeName.getFullyQualifiedName();
        if (annotationTypeName.isQualifiedName()) {
            annotationName = ((QualifiedName) annotationTypeName).getName().getFullyQualifiedName();
        }
        return annotationName;
    }

    private static boolean compareAnnotations(Annotation newAnnotation, Annotation existingAnnotation) {
        return AnnotationUtils.getAnnotationName(existingAnnotation).equals(
                AnnotationUtils.getAnnotationName(newAnnotation));
    }

    @SuppressWarnings("unchecked")
    private static boolean isAnnotationPresent(BodyDeclaration bodyDeclaration, Annotation annatotationToAdd) {
        boolean exists = false;
        List<IExtendedModifier> modifiers = bodyDeclaration.modifiers();
        for (IExtendedModifier extendedModifier : modifiers) {
            if (extendedModifier instanceof Annotation) {
                Annotation existingAnnotation = (Annotation) extendedModifier;
                if (compareAnnotations(annatotationToAdd, existingAnnotation)) {
                    return true;
                }
            }
        }
        return exists;
    }

    @SuppressWarnings("unchecked")
    public static boolean isAnnotationPresent(final IMethod method, final String annotationKey) {
        ICompilationUnit source = method.getCompilationUnit();
        CompilationUnit compilationUnit = getASTParser(source);
        final List<MethodDeclaration> methodDeclarations = new ArrayList<MethodDeclaration>();
        compilationUnit.accept(new ASTVisitor() {
            @Override
            public boolean visit(MethodDeclaration methodDeclaration) {
                if (methodDeclaration.getName().getIdentifier().equals(method.getElementName())) {
                    methodDeclarations.add(methodDeclaration);
                }
                return super.visit(methodDeclaration);
            }
        });

        for (MethodDeclaration methodDeclaration : methodDeclarations) {
            if (annotationKey.equals(AnnotationUtils.WEB_PARAM)) {
                List<SingleVariableDeclaration> parameters = methodDeclaration.parameters();
                for (SingleVariableDeclaration singleVariableDeclaration : parameters) {
                    if (compareModifiers(singleVariableDeclaration.modifiers(), annotationKey)) {
                        return true;
                    }
                }
            } else {
                 return compareModifiers(methodDeclaration.modifiers(), annotationKey);
            }

        }
        return false;
    }
    
    @SuppressWarnings("unchecked")
    private static boolean isAnnotationPresent(SingleVariableDeclaration parameter,
            Annotation annatotationToAdd) {
        boolean exists = false;
        List<IExtendedModifier> modifiers = parameter.modifiers();
        for (IExtendedModifier extendedModifier : modifiers) {
            if (extendedModifier instanceof Annotation) {
                Annotation existingAnnotation = (Annotation) extendedModifier;
                if (compareAnnotations(annatotationToAdd, existingAnnotation)) {
                    return true;
                }
            }
        }
        return exists;
    }

    private static boolean compareMethodParameters(SingleVariableDeclaration paramOne,
            SingleVariableDeclaration paramTwo) {
        String typeOne = paramOne.getType().toString();
        String nameOne = paramOne.getName().getIdentifier();

        String typeTwo = paramTwo.getType().toString();
        String nameTwo = paramTwo.getName().getIdentifier();

        return (typeOne.equals(typeTwo)) && (nameOne.equals(nameTwo));
    }

    private static boolean compareModifiers(List<IExtendedModifier> modifiers, String annotationKey) {
        for (IExtendedModifier extendedModifier : modifiers) {
            if (extendedModifier instanceof Annotation) {
                Annotation existingAnnotation = (Annotation) extendedModifier;
                String annotationName = AnnotationUtils.getAnnotationName(existingAnnotation);
                if (annotationName.equals(annotationKey)) {
                    return true;
                }
            }
        }
        return false;
    }
    
    public static Map<String, Boolean> getAnnotationMap(Java2WSDataModel model) {
        Map<String, Boolean> annotationdMap = new HashMap<String, Boolean>();
        annotationdMap.put(AnnotationUtils.WEB_METHOD, model.isGenerateWebMethodAnnotation());
        annotationdMap.put(AnnotationUtils.WEB_PARAM, model.isGenerateWebParamAnnotation());
        annotationdMap.put(AnnotationUtils.REQUEST_WRAPPER, model.isGenerateRequestWrapperAnnotation());
        annotationdMap.put(AnnotationUtils.RESPONSE_WRAPPER, model.isGenerateWebParamAnnotation());
        return annotationdMap;
    }
    
    /**
     * Loads all public methods with the default annotation maps
     * @return
     */
    public static Map<IMethod, Map<String, Boolean>> getMethodMap(IType type, Java2WSDataModel model) {
        Map<IMethod, Map<String, Boolean>> methodMap = new HashMap<IMethod, Map<String, Boolean>>();

        try {
            IMethod[] methods = type.getMethods();
            for (IMethod method : methods) {
                if (JDTUtils.isPublicSMethod(method)) {
                    methodMap.put(method, getAnnotationMap(model));
                }
            }
        } catch (JavaModelException jme) {
            CXFCorePlugin.log(jme.getStatus());
        }
        return methodMap;
    }
}