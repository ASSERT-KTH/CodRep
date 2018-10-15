textFileChange.addEdit(AnnotationUtils.createAddImportTextEdit(source.findPrimaryType(), WebService.class.getCanonicalName()));

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
package org.eclipse.jst.ws.jaxws.core.tests;

import java.util.ArrayList;
import java.util.List;

import javax.jws.WebService;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jdt.core.dom.MemberValuePair;
import org.eclipse.jst.ws.annotations.core.AnnotationsCore;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;

public class AddAnnotationToTypeTest extends AbstractAnnotationTest {

    @Override
    public String getPackageName() {
        return "com.example";
    }

    @Override
    public String getClassName() {
        return "Calculator.java";
    }

    @Override
    public String getClassContents() {
        StringBuilder classContents = new StringBuilder("package com.example;\n\n");
        classContents.append("public class Calculator {\n\n\tpublic int add(int i, int k) {");
        classContents.append("\n\t\treturn i + k;\n\t}\n}");
        return classContents.toString();
    }

    @Override
    public Annotation getAnnotation() {
        List<MemberValuePair> memberValuePairs = new ArrayList<MemberValuePair>();

        MemberValuePair nameValuePair = AnnotationsCore
                .createStringMemberValuePair(ast, "name", "Calculator");

        MemberValuePair targetNamespaceValuePair = AnnotationsCore.createStringMemberValuePair(ast,
                "targetNamespace", JDTUtils.getTargetNamespaceFromPackageName(getPackageName()));

        MemberValuePair portNameValuePair = AnnotationsCore.createStringMemberValuePair(ast, "portName",
                "CalculatorPort");

        MemberValuePair serviceNameValuePair = AnnotationsCore.createStringMemberValuePair(ast,
                "serviceName", "CalculatorService");

        memberValuePairs.add(nameValuePair);
        memberValuePairs.add(targetNamespaceValuePair);
        memberValuePairs.add(portNameValuePair);
        memberValuePairs.add(serviceNameValuePair);

        return AnnotationsCore.createNormalAnnotation(ast, WebService.class.getSimpleName(), memberValuePairs);
    }

    public void testAddAnnotationToType() {
        try {
            assertNotNull(annotation);
            assertEquals(WebService.class.getSimpleName(), AnnotationUtils.getAnnotationName(annotation));

            textFileChange.addEdit(AnnotationUtils.createAddImportTextEdit(source.findPrimaryType(), WebService.class));
            textFileChange.addEdit(AnnotationUtils.createAddAnnotationTextEdit(source.findPrimaryType(), annotation));

            assertTrue(executeChange(new NullProgressMonitor(), textFileChange));
 
            assertTrue(AnnotationUtils.isAnnotationPresent(source, AnnotationUtils.getAnnotationName(annotation)));
            assertTrue(source.getImport(WebService.class.getCanonicalName()).exists());
        } catch (CoreException ce) {
            fail(ce.getLocalizedMessage());
        }
    }
}