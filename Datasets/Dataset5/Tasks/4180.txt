private static Pattern pattern = Pattern.compile("arg\\d++"); //$NON-NLS-1$

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

import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.CLASS_NAME;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.FAULT_BEAN;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.HEADER;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.LOCAL_NAME;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.MODE;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.NAME;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.OPERATION_NAME;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.RESPONSE_SUFFIX;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.TARGET_NAMESPACE;

import java.lang.annotation.Annotation;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.jws.WebMethod;
import javax.jws.WebParam;
import javax.jws.WebResult;
import javax.jws.WebService;
import javax.jws.WebParam.Mode;
import javax.jws.soap.SOAPBinding;
import javax.xml.namespace.QName;
import javax.xml.ws.Holder;
import javax.xml.ws.RequestWrapper;
import javax.xml.ws.ResponseWrapper;
import javax.xml.ws.WebFault;

import org.apache.xerces.util.XMLChar;
import org.eclipse.jst.ws.annotations.core.processor.AbstractAnnotationProcessor;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.internal.jaxws.core.JAXWSCoreMessages;
import org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils;
import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;

import com.sun.mirror.declaration.AnnotationMirror;
import com.sun.mirror.declaration.AnnotationTypeDeclaration;
import com.sun.mirror.declaration.AnnotationValue;
import com.sun.mirror.declaration.ClassDeclaration;
import com.sun.mirror.declaration.Declaration;
import com.sun.mirror.declaration.MethodDeclaration;
import com.sun.mirror.declaration.ParameterDeclaration;
import com.sun.mirror.declaration.TypeDeclaration;
import com.sun.mirror.type.ReferenceType;
import com.sun.mirror.type.TypeMirror;
import com.sun.mirror.util.SourcePosition;

public class UniqueNamesRule extends AbstractAnnotationProcessor {
    private static Pattern pattern = Pattern.compile("arg\\d++");
    
    @Override
    public void process() {
        AnnotationTypeDeclaration webServiceDeclaration = (AnnotationTypeDeclaration) environment
                .getTypeDeclaration(WebService.class.getName());

        Collection<Declaration> annotatedTypes = environment
                .getDeclarationsAnnotatedWith(webServiceDeclaration);

        for (Declaration declaration : annotatedTypes) {
            if (declaration instanceof TypeDeclaration) {
                TypeDeclaration typeDeclaration = (TypeDeclaration) declaration;
                checkOperationNames(typeDeclaration.getMethods());
                checkWrapperAndFaultBeanNames(typeDeclaration.getMethods());
                checkDocumentBareMethods(typeDeclaration.getMethods());
                checkMethodParameters(typeDeclaration.getMethods());
            }
        }
    }
    
    private void checkOperationNames(Collection<? extends MethodDeclaration> methods) {
        Map<Declaration, QName> nameMap = new HashMap<Declaration, QName>();
        for (MethodDeclaration methodDeclaration : methods) {
            nameMap.put(methodDeclaration, new QName(getTargetNamespace(methodDeclaration.getDeclaringType()), 
                    getOperationName(methodDeclaration)));
        }
        
        Declaration[] keys = nameMap.keySet().toArray(new Declaration[nameMap.size()]);
        QName[] values = nameMap.values().toArray(new QName[nameMap.size()]);

        for (int i = 0; i < values.length; i++) {
            QName qName = values[i];
            validateName(qName, keys[i]);
            for (int j = i + 1; j < values.length; j++) {
                QName otherQName = values[j];
                if (qName.equals(otherQName)) {
                    printError(keys[i].getPosition(), JAXWSCoreMessages.bind(
                            JAXWSCoreMessages.OPERATION_NAMES_MUST_BE_UNIQUE_ERROR, qName));
                    printError(keys[j].getPosition(), JAXWSCoreMessages.bind(
                            JAXWSCoreMessages.OPERATION_NAMES_MUST_BE_UNIQUE_ERROR, otherQName));
                }
            }
        }
    }
        
    private String getAttributeValue(Declaration declaration, Class<? extends Annotation> annotation, String attributeName) {
        AnnotationMirror annotationMirror = AnnotationUtils.getAnnotation(declaration, annotation);
        if (annotationMirror != null) {
            return AnnotationUtils.getStringValue(annotationMirror, attributeName);
        }
        return null;
    }

    private void checkWrapperAndFaultBeanNames(Collection<? extends MethodDeclaration> methodDeclarations) {
        AnnotationTypeDeclaration requestWrapperDeclaration = (AnnotationTypeDeclaration) environment
                .getTypeDeclaration(RequestWrapper.class.getName());

        AnnotationTypeDeclaration resposeWrapperDeclaration = (AnnotationTypeDeclaration) environment
                .getTypeDeclaration(ResponseWrapper.class.getName());

        Set<Declaration> methods = new HashSet<Declaration>();
        methods.addAll(environment.getDeclarationsAnnotatedWith(requestWrapperDeclaration));
        methods.addAll(environment.getDeclarationsAnnotatedWith(resposeWrapperDeclaration));

        List<AnnotationValue> classNames = new ArrayList<AnnotationValue>();
        Map<Object, QName> qNames = new HashMap<Object, QName>();

        for (Declaration declaration : methods) {
            AnnotationMirror requestWrapper = AnnotationUtils.getAnnotation(declaration, RequestWrapper.class);
            if (requestWrapper != null) {
                addClassName(requestWrapper, CLASS_NAME, classNames);
                addLocalName(requestWrapper, LOCAL_NAME, declaration, qNames);
            }
            
            AnnotationMirror responseWrapper = AnnotationUtils.getAnnotation(declaration, ResponseWrapper.class);
            if (responseWrapper != null) {
                addClassName(responseWrapper, CLASS_NAME, classNames);
                addLocalName(responseWrapper, LOCAL_NAME, declaration, qNames);
            }
        }
        
        Set<ReferenceType> thrownTypes = new HashSet<ReferenceType>();
        
        for (MethodDeclaration methodDeclaration : methodDeclarations) {
            thrownTypes.addAll(methodDeclaration.getThrownTypes());
        }

        for (ReferenceType referenceType : thrownTypes) {
            if (referenceType instanceof ClassDeclaration) {
                ClassDeclaration classDeclaration = (ClassDeclaration) referenceType;
                AnnotationMirror webFault = AnnotationUtils.getAnnotation(classDeclaration, WebFault.class);
                if (webFault != null) {
                   addClassName(webFault, FAULT_BEAN, classNames);
                }
            }
        }

        for (int i = 0; i < classNames.size(); i++) {
            AnnotationValue className = classNames.get(i);
            for (int j = i + 1; j < classNames.size(); j++) {
                AnnotationValue otherClassName = classNames.get(j);
                if (className.getValue().toString().equalsIgnoreCase(otherClassName.getValue().toString())) {
                    printError(className.getPosition(), JAXWSCoreMessages.bind(
                            JAXWSCoreMessages.WRAPPER_FAULT_BEAN_NAMES_MUST_BE_UNIQUE, className));
                    printError(otherClassName.getPosition(), JAXWSCoreMessages.bind(
                            JAXWSCoreMessages.WRAPPER_FAULT_BEAN_NAMES_MUST_BE_UNIQUE, otherClassName));
                }
            }
        }
        
        validateQNames(qNames, JAXWSCoreMessages.LOCAL_NAME_ATTRIBUTES_MUST_BE_UNIQUE);
    }
    
    private void validateQNames(Map<Object, QName> qNames, String errorMessage) {
        Object[] keys =  qNames.keySet().toArray(new Object[qNames.size()]);
        QName[] values = qNames.values().toArray(new QName[qNames.size()]);
       
        for(int i = 0; i < values.length; i++) {
            QName qName = values[i];
            validateName(qName, keys[i]);
            for(int j = i + 1; j < values.length; j++) {
                QName otherQName = values[j];
                if (qName.equals(otherQName)) {
                    printError(getPosition(keys[i]), JAXWSCoreMessages.bind(errorMessage, qName));
                    printError(getPosition(keys[j]), JAXWSCoreMessages.bind(errorMessage, otherQName));
                }
            }
        }
    }
    
    private void addClassName(AnnotationMirror annotationMirror, String attributeKey,
            List<AnnotationValue> classNames) {
        AnnotationValue className = AnnotationUtils.getAnnotationValue(annotationMirror, attributeKey);
        if (className != null) {
            classNames.add(className);
        }
    }

    private void addLocalName(AnnotationMirror annotationMirror, String attributeKey, 
            Declaration declaration, Map<Object, QName> qNames) {
        AnnotationValue localNameValue = AnnotationUtils.getAnnotationValue(annotationMirror, attributeKey);
        if (localNameValue != null) {
            qNames.put(localNameValue, new QName(getTargetNamespace(annotationMirror, 
                    (MethodDeclaration)declaration), localNameValue.getValue().toString()));
        }    
    }

    private void checkDocumentBareMethods(Collection<? extends MethodDeclaration> methods) {
        List<MethodDeclaration> docBareMethods = new ArrayList<MethodDeclaration>();
        for (MethodDeclaration methodDeclaration : methods) {
            if (hasDocumentBareSOAPBinding(methodDeclaration)) {
                docBareMethods.add(methodDeclaration);
            }
        }
        
        Map<Object, QName> qNames = new HashMap<Object, QName>();
        for (MethodDeclaration methodDeclaration : docBareMethods) {
            getDocumentBareOperationRequest(methodDeclaration, qNames);
            getDocumentBareOperationResponse(methodDeclaration, qNames);            
        }
        
        validateQNames(qNames, JAXWSCoreMessages.DOC_BARE_METHODS_UNIQUE_XML_ELEMENTS);
    }

    private SourcePosition getPosition(Object value) {
        if (value instanceof AnnotationValue) {
            return ((AnnotationValue) value).getPosition();
        }
        if (value instanceof MethodDeclaration) {
            return ((MethodDeclaration) value).getPosition();
        }
        if (value instanceof ParameterDeclaration) {
            return ((ParameterDeclaration) value).getPosition();
        }
        return null;
    }
    
    private void validateName(QName qName, Object object) {
        String name = qName.getLocalPart();
        if (name.trim().length() > 0) {
            if (!XMLChar.isValidNCName(name)) {
                printError(getPosition(object), JAXWSCoreMessages.bind(
                        JAXWSCoreMessages.INVALID_NAME_ATTRIBUTE, name));
            }
        }
    }

    private void validateName(AnnotationValue value) {
        String name = value.getValue().toString();
        if (name.trim().length() > 0) {
            if (!XMLChar.isValidNCName(name)) {
                printError(value.getPosition(), JAXWSCoreMessages.bind(
                        JAXWSCoreMessages.INVALID_NAME_ATTRIBUTE, name));
            }
        }
    }

    private void getDocumentBareOperationRequest(MethodDeclaration methodDeclaration, Map<Object, QName> qNames) {
        Collection<ParameterDeclaration> parameters = methodDeclaration.getParameters();
        for (ParameterDeclaration parameterDeclaration : parameters) {
            AnnotationMirror webParam = AnnotationUtils.getAnnotation(parameterDeclaration, WebParam.class);
            if (webParam != null) {
                String mode = getWebParamMode(webParam, parameterDeclaration);
                if (mode.equals(Mode.IN.name()) || mode.equals(Mode.INOUT.name())) {
                    getOperationRequest(webParam, methodDeclaration, parameterDeclaration, qNames);
                }
            } else {
                qNames.put(parameterDeclaration, getOperationRequestDefault(methodDeclaration));
            }
        }
    }
    
    private void getOperationRequest(AnnotationMirror annotationMirror, MethodDeclaration methodDeclaration,
            ParameterDeclaration parameterDeclaration, Map<Object, QName> qNames) {
        AnnotationValue name = AnnotationUtils.getAnnotationValue(annotationMirror, NAME);
        if (name != null) {
            QName qName = new QName(getTargetNamespace(annotationMirror, methodDeclaration), name.getValue()
                    .toString());
            qNames.put(name, qName);
        } else {
            qNames.put(parameterDeclaration, getOperationRequestDefault(methodDeclaration));
        }
    }

    private QName getOperationRequestDefault(MethodDeclaration methodDeclaration) {
        return new QName(getTargetNamespace(methodDeclaration.getDeclaringType()), methodDeclaration
                .getSimpleName());
    }
    
    private void getDocumentBareOperationResponse(MethodDeclaration methodDeclaration, Map<Object, QName> qNames) {
        if (!returnsVoid(methodDeclaration)) {
            getOperationResponse(AnnotationUtils.getAnnotation(methodDeclaration, WebResult.class),
                    methodDeclaration, qNames);
        } else {
            Collection<ParameterDeclaration> parameters = methodDeclaration.getParameters();
            for (ParameterDeclaration parameterDeclaration : parameters) {
                AnnotationMirror webParam = AnnotationUtils.getAnnotation(parameterDeclaration, WebParam.class);
                if (webParam != null) {
                    String mode = getWebParamMode(webParam, parameterDeclaration);
                    if (mode.equals(Mode.OUT.name()) || mode.equals(Mode.INOUT.name()) && !isHeader(webParam)) {
                        getOperationResponse(webParam, methodDeclaration, qNames);
                        break;
                    }
                } else if (getDefaultWebParamMode(parameterDeclaration).equals(Mode.INOUT.name())) {
                    qNames.put(parameterDeclaration, getOperationResponseDefault(methodDeclaration));
                    break;
                }
            }
        }
    }
    
    private void getOperationResponse(AnnotationMirror annotationMirror, MethodDeclaration methodDeclaration,
            Map<Object, QName> qNames) {
        if (annotationMirror != null) {
            AnnotationValue name = AnnotationUtils.getAnnotationValue(annotationMirror, NAME);
            if (name != null) {
                qNames.put(name, new QName(getTargetNamespace(annotationMirror, methodDeclaration), name
                        .getValue().toString()));
            } else {
                qNames.put(methodDeclaration, getOperationResponseDefault(methodDeclaration));
            }
        } else {
            qNames.put(methodDeclaration, getOperationResponseDefault(methodDeclaration));
        }
    }
    
    private QName getOperationResponseDefault(MethodDeclaration methodDeclaration) {
        return new QName(getTargetNamespace(methodDeclaration.getDeclaringType()), methodDeclaration
                .getSimpleName()
                + RESPONSE_SUFFIX);
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

    private boolean returnsVoid(MethodDeclaration methodDeclaration) {
        return methodDeclaration.getReturnType().equals(environment.getTypeUtils().getVoidType()); 
    }
    
    private void checkMethodParameters(Collection<? extends MethodDeclaration> methodDeclarations) {
        List<MethodDeclaration> methods = new ArrayList<MethodDeclaration>();
        for (MethodDeclaration methodDeclaration : methodDeclarations) {
            //Not Doc Bare
            if (!hasDocumentBareSOAPBinding(methodDeclaration)) {
                methods.add(methodDeclaration);
            }
        }
        
        for (MethodDeclaration methodDeclaration : methods) {
            List<AnnotationValue> names = new ArrayList<AnnotationValue>();
            List<ParameterDeclaration> parameters = (List<ParameterDeclaration>) methodDeclaration.getParameters();
            for (ParameterDeclaration parameterDeclaration : parameters) {
                AnnotationMirror webParam = AnnotationUtils.getAnnotation(parameterDeclaration, WebParam.class);
                if (webParam != null) {
                    AnnotationValue name = AnnotationUtils.getAnnotationValue(webParam, NAME);
                    if (name != null) {
                        names.add(name);
                        testForGeneratedNameClash(name, parameterDeclaration, parameters);
                    }
                }
            }
            
            for (int i = 0; i < names.size(); i++) {
                AnnotationValue name = names.get(i);
                validateName(name);
                for (int j = i + 1; j < names.size(); j++) {
                    AnnotationValue otherName = names.get(j);
                    if (name.toString().equals(otherName.toString())) {
                        printError(name.getPosition(), JAXWSCoreMessages.bind(
                                JAXWSCoreMessages.PARAMETER_NAME_CLASH, name.getValue().toString()));
                        printError(otherName.getPosition(), JAXWSCoreMessages.bind(
                                JAXWSCoreMessages.PARAMETER_NAME_CLASH, otherName.getValue().toString()));
                    }
                }
            }
        }
    }

    private void testForGeneratedNameClash(AnnotationValue webParamName, ParameterDeclaration parameter,
            List<ParameterDeclaration> parameters) {
        String name = webParamName.toString();
        Matcher matcher = pattern.matcher(name);
        if (matcher.matches()) {
            int argN = Integer.parseInt(name.substring(3));
            if (argN != parameters.indexOf(parameter)) {
                if (argN < parameters.size()) {
                    ParameterDeclaration parameterN = parameters.get(argN);
                    AnnotationMirror webParamN = AnnotationUtils.getAnnotation(parameterN, WebParam.class);
                    if (webParamN != null) {
                        AnnotationValue webParamNameN = AnnotationUtils.getAnnotationValue(webParamN, NAME);
                        if (webParamNameN == null) {
                            printError(parameterN.getPosition(), JAXWSCoreMessages.bind(
                                    JAXWSCoreMessages.GENERATED_PARAMETER_NAME_CLASH, name));
                            printError(webParamName.getPosition(), JAXWSCoreMessages.bind(
                                    JAXWSCoreMessages.GENERATED_PARAMETER_NAME_CLASH, name));
                        } else if (webParamNameN.toString().length() == 0) {
                            printError(webParamNameN.getPosition(), JAXWSCoreMessages.bind(
                                    JAXWSCoreMessages.GENERATED_PARAMETER_NAME_CLASH, name));
                            printError(webParamName.getPosition(), JAXWSCoreMessages.bind(
                                    JAXWSCoreMessages.GENERATED_PARAMETER_NAME_CLASH, name));
                        }
                    } else {
                        printError(parameterN.getPosition(), JAXWSCoreMessages.bind(
                                JAXWSCoreMessages.GENERATED_PARAMETER_NAME_CLASH, name));
                        printError(webParamName.getPosition(), JAXWSCoreMessages.bind(
                                JAXWSCoreMessages.GENERATED_PARAMETER_NAME_CLASH, name));
                    }
                }
            }
        }
    }
    
    private String getTargetNamespace(TypeDeclaration typeDeclaration) {
        String targetNamespace = getAttributeValue(typeDeclaration, WebService.class, TARGET_NAMESPACE);
        if (targetNamespace != null) {
            return targetNamespace;
        }
        
        return JDTUtils.getTargetNamespaceFromPackageName(typeDeclaration.getPackage().getQualifiedName());
    }
    
    private String getTargetNamespace(AnnotationMirror annotationMirror, MethodDeclaration methodDeclaration) {
        String targetNamespace = AnnotationUtils.getStringValue(annotationMirror, TARGET_NAMESPACE);
        if (targetNamespace == null) {
            targetNamespace = getTargetNamespace(methodDeclaration.getDeclaringType());
        }
        return targetNamespace;
    }

    private String getOperationName(MethodDeclaration methodDeclaration) {
        String operationName = getAttributeValue(methodDeclaration, WebMethod.class, OPERATION_NAME);
        if (operationName != null) {
            return operationName;
        }
        return methodDeclaration.getSimpleName();
    }

    private boolean hasDocumentBareSOAPBinding(Declaration declaration) {
        AnnotationMirror soapBinding = AnnotationUtils.getAnnotation(declaration, SOAPBinding.class);
        if (soapBinding != null) {
            return JAXWSUtils.isDocumentBare(soapBinding);
        }
        if (declaration instanceof MethodDeclaration) {
            MethodDeclaration methodDeclaration = (MethodDeclaration) declaration;
            return hasDocumentBareSOAPBinding(methodDeclaration.getDeclaringType());
        }
        
        return false;
    }
}