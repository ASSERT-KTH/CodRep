assertEquals(JAXWSCoreMessages.WEBSERVICE_ENPOINTINTERFACE_NO_WEBMETHODS_ERROR_MESSAGE,

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
package org.eclipse.jst.ws.jaxws.core.annotation.validation.tests;

import org.eclipse.core.resources.IMarker;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.core.runtime.OperationCanceledException;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jst.ws.annotations.core.AnnotationsCore;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.internal.jaxws.core.JAXWSCoreMessages;

/**
 * 
 * @author sclarke
 * 
 */
public class WebServiceSEIPresentNoWebMethodRuleTest extends AbstractAnnotationValidationTest {

    @Override
    protected Annotation getAnnotation() {
        return AnnotationsCore.createAnnotation(ast, javax.jws.WebMethod.class, javax.jws.WebMethod.class
                .getSimpleName(), null);
    }

    @Override
    protected String getClassContents() {
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
    protected String getClassName() {
        return "MyClass.java";
    }

    @Override
    protected String getPackageName() {
        return "com.example";
    }

    public void testWebServiceSEIPresentNoWebMethodRule() {
        try {
            assertNotNull(annotation);
            assertEquals("WebMethod", AnnotationUtils.getAnnotationName(annotation));

            IMethod method = source.findPrimaryType().getMethod("myMethod", new String[0]);
            assertNotNull(method);

            AnnotationUtils.getImportChange(compilationUnit, javax.jws.WebMethod.class, textFileChange, true);

            AnnotationUtils.createMethodAnnotationChange(source, compilationUnit, rewriter, method,
                    annotation, textFileChange);

            assertTrue(executeChange(new NullProgressMonitor(), textFileChange));

            assertTrue(AnnotationUtils.isAnnotationPresent(method, AnnotationUtils
                    .getAnnotationName(annotation)));

            Job.getJobManager().join(ResourcesPlugin.FAMILY_AUTO_BUILD, null);

            IMarker[] allmarkers = source.getResource().findMarkers(IMarker.PROBLEM, true,
                    IResource.DEPTH_INFINITE);

            assertEquals(1, allmarkers.length);

            IMarker annotationProblemMarker = allmarkers[0];

            assertEquals(source.getResource(), annotationProblemMarker.getResource());
            assertEquals(JAXWSCoreMessages.WEBSERVICE_ENPOINTINTERFACE_NO_WEBMETHOS_ERROR_MESSAGE,
                    annotationProblemMarker.getAttribute(IMarker.MESSAGE));
        } catch (CoreException ce) {
            fail(ce.getLocalizedMessage());
        } catch (OperationCanceledException oce) {
            fail(oce.getLocalizedMessage());
        } catch (InterruptedException ie) {
            fail(ie.getLocalizedMessage());
        }
    }

}