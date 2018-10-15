textFileChange.addEdit(AnnotationUtils.createRemoveImportTextEdit(method, WebMethod.class.getCanonicalName()));

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

import javax.jws.WebMethod;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jst.ws.annotations.core.AnnotationsCore;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;

public class RemoveAnnotationFromMethodTest extends AbstractAnnotationTest {

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
        classContents.append("import javax.jws.WebMethod;\n\n");
        classContents.append("public class Calculator {\n\n\t@WebMethod\n\tpublic int add(int i, int k) {");
        classContents.append("\n\t\treturn i + k;\n\t}\n}");
        return classContents.toString();
    }

    @Override
    public Annotation getAnnotation() {
        return AnnotationsCore.createNormalAnnotation(ast, WebMethod.class.getSimpleName(), null);
    }

    public void testRemoveAnnotationFromMethod() {
        try {
            assertNotNull(annotation);
            assertEquals(WebMethod.class.getSimpleName(), AnnotationUtils.getAnnotationName(annotation));

            IMethod method = source.findPrimaryType().getMethod("add", new String[] { "I", "I" });
            assertNotNull(method);

            assertTrue(AnnotationUtils.isAnnotationPresent(method, AnnotationUtils
                    .getAnnotationName(annotation)));
            assertNotNull(source.getImport(WebMethod.class.getCanonicalName()));
            
            textFileChange.addEdit(AnnotationUtils.createRemoveAnnotationTextEdit(method, annotation));
            textFileChange.addEdit(AnnotationUtils.createRemoveImportTextEdit(method, WebMethod.class));

            assertTrue(executeChange(new NullProgressMonitor(), textFileChange));

            assertFalse(AnnotationUtils.isAnnotationPresent(method, AnnotationUtils
                    .getAnnotationName(annotation)));
            assertFalse(source.getImport(WebMethod.class.getCanonicalName()).exists());
        } catch (CoreException ce) {
            fail(ce.getLocalizedMessage());
        }
    }
}