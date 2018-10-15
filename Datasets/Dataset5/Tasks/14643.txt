textFileChange.addEdit(AnnotationUtils.createAddImportTextEdit(field, WebServiceRef.class.getCanonicalName()));

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

import javax.xml.ws.WebServiceRef;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.IField;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jdt.core.dom.MemberValuePair;
import org.eclipse.jst.ws.annotations.core.AnnotationsCore;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;

public class AddAnnotationToFieldTest extends AbstractAnnotationTest {

    @Override
    public String getPackageName() {
        return "com.example";
    }

    @Override
    public String getClassName() {
        return "MyClass.java";
    }

    @Override
    public String getClassContents() {
        return "package com.example;\n\npublic class MyClass {\n\n\tstatic String service;\n\n}";
    }

    @Override
    public Annotation getAnnotation() {
        List<MemberValuePair> memberValuePairs = new ArrayList<MemberValuePair>();

        MemberValuePair wsdlLocationValuePair = AnnotationsCore.createStringMemberValuePair(ast,
                "wsdlLocation", "http://localhost:8083/ServiceProject/servives/MyService?WSDL");

        memberValuePairs.add(wsdlLocationValuePair);

        return AnnotationsCore.createNormalAnnotation(ast, WebServiceRef.class.getSimpleName(), memberValuePairs);
    }

    public void testAddAnnotationToField() {
        try {
            assertNotNull(annotation);
            assertEquals(WebServiceRef.class.getSimpleName(), AnnotationUtils.getAnnotationName(annotation));

            IField field = source.findPrimaryType().getField("service");
            assertNotNull(field);

            textFileChange.addEdit(AnnotationUtils.createAddImportTextEdit(field, WebServiceRef.class));
            textFileChange.addEdit(AnnotationUtils.createAddAnnotationTextEdit(field, annotation));

            assertTrue(executeChange(new NullProgressMonitor(), textFileChange));

            assertTrue(AnnotationUtils.isAnnotationPresent(field, AnnotationUtils.getAnnotationName(annotation)));
            assertTrue(source.getImport(WebServiceRef.class.getCanonicalName()).exists());
        } catch (CoreException ce) {
            fail(ce.getLocalizedMessage());
        }
    }
    
}