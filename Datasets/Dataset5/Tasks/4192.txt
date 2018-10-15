.getCompilationUnit(), false), method, 93);

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

import javax.jws.WebParam;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jst.ws.annotations.core.AnnotationsCore;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;

public class RemoveAnnotationFromMethodParameterTest extends AbstractAnnotationTest {

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
        classContents.append("import javax.jws.WebParam;\n\n");
        classContents.append("public class Calculator {\n\n\tpublic int add(@WebParam(name=\"i\")");
        classContents.append("int i, int k) {\n\t\treturn i + k;\n\t}\n}");
        return classContents.toString();
    }

    @Override
    public Annotation getAnnotation() {
        return AnnotationsCore.createAnnotation(ast, WebParam.class, WebParam.class.getSimpleName(), null);
    }

    public void testRemoveAnnotationFromMethodParameter() {
        try {
            assertNotNull(annotation);
            assertEquals(WebParam.class.getSimpleName(), AnnotationUtils.getAnnotationName(annotation));

            IMethod method = source.findPrimaryType().getMethod("add", new String[] { "I", "I" });
            assertNotNull(method);

            SingleVariableDeclaration parameter = AnnotationUtils.getMethodParameter(compilationUnit, method,
                    93);

            assertTrue(AnnotationUtils.isAnnotationPresent(parameter, annotation));

            AnnotationUtils.removeAnnotationFromMethodParameter(source, rewriter, parameter, annotation,
                    textFileChange);

            assertTrue(executeChange(new NullProgressMonitor(), textFileChange));

            // refresh
            parameter = AnnotationUtils.getMethodParameter(AnnotationUtils.getASTParser(method
                    .getCompilationUnit()), method, 93);

            assertFalse(AnnotationUtils.isAnnotationPresent(parameter, annotation));
        } catch (CoreException ce) {
            fail(ce.getLocalizedMessage());
        }
    }
}
 No newline at end of file