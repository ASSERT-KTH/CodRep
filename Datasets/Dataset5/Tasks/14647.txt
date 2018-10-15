textFileChange.addEdit(AnnotationUtils.createRemoveImportTextEdit(field, WebServiceRef.class.getCanonicalName()));

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

import javax.xml.ws.WebServiceRef;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.IField;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jst.ws.annotations.core.AnnotationsCore;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;

public class RemoveAnnotationFromFieldTest extends AbstractAnnotationTest {

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
        StringBuilder classContents = new StringBuilder("package com.example;\n\n");
        classContents.append("import javax.xml.ws.WebServiceRef;\n\n");
        classContents.append("public class MyClass {\n\n\t@WebServiceRef()\n\tstatic String service;\n\n}");
        return classContents.toString();
    }

    @Override
    public Annotation getAnnotation() {
        return AnnotationsCore.createNormalAnnotation(ast, WebServiceRef.class.getSimpleName(), null);
    }

    public void testRemoveAnnotationFromField() {
        try {
            assertNotNull(annotation);
            assertEquals(WebServiceRef.class.getSimpleName(), AnnotationUtils.getAnnotationName(annotation));

            IField field = source.findPrimaryType().getField("service");
            assertNotNull(field);

            assertTrue(AnnotationUtils.isAnnotationPresent(field, AnnotationUtils
                    .getAnnotationName(annotation)));
            
            assertNotNull(source.getImport(WebServiceRef.class.getCanonicalName()));
            
            textFileChange.addEdit(AnnotationUtils.createRemoveAnnotationTextEdit(field, annotation));
            textFileChange.addEdit(AnnotationUtils.createRemoveImportTextEdit(field, WebServiceRef.class));
            
            assertTrue(executeChange(new NullProgressMonitor(), textFileChange));

            assertFalse(AnnotationUtils.isAnnotationPresent(field, AnnotationUtils.getAnnotationName(annotation)));
            assertFalse(source.getImport(WebServiceRef.class.getCanonicalName()).exists());
        } catch (CoreException ce) {
            fail(ce.getLocalizedMessage());
        }
    }
}