textFileChange.addEdit(AnnotationUtils.createRemoveImportTextEdit(source.findPrimaryType(), WebService.class.getCanonicalName()));

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

import javax.jws.WebService;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jst.ws.annotations.core.AnnotationsCore;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;

public class RemoveAnnotationFromTypeTest extends AbstractAnnotationTest {

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
        classContents.append("import javax.jws.WebService;\n\n");
        classContents.append("@WebService(name=\"MyClass\", endpointInterface=\"MyInterface\", ");
        classContents.append("targetNamespace=\"http://example.com/\", portName=\"MyClassPort\", ");
        classContents.append("serviceName=\"MyClassService\")\n");
        classContents.append("public class MyClass {\n\n");
        classContents.append("\tpublic String myMethod() {" + "\n\t\treturn \"txt\";\n\t}\n\n}");
        return classContents.toString();
    }

    @Override
    public Annotation getAnnotation() {
        return AnnotationsCore.createNormalAnnotation(ast, WebService.class.getSimpleName(), null);
    }

    public void testRemoveAnnotationFromType() {
        try {
            assertNotNull(annotation);
            assertEquals(WebService.class.getSimpleName(), AnnotationUtils.getAnnotationName(annotation));

            assertTrue(AnnotationUtils.isAnnotationPresent(source, AnnotationUtils.getAnnotationName(annotation)));
            assertNotNull(source.getImport(WebService.class.getCanonicalName()));
            
            textFileChange.addEdit(AnnotationUtils.createRemoveAnnotationTextEdit(source.findPrimaryType(), annotation));
            textFileChange.addEdit(AnnotationUtils.createRemoveImportTextEdit(source.findPrimaryType(), WebService.class));

            assertTrue(executeChange(new NullProgressMonitor(), textFileChange));

            assertFalse(AnnotationUtils.isAnnotationPresent(source, AnnotationUtils.getAnnotationName(annotation)));
            assertFalse(source.getImport(WebService.class.getCanonicalName()).exists());
        } catch (CoreException ce) {
            fail(ce.getLocalizedMessage());
        }
    }
}