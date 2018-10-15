.getCompilationUnit(), false), method, 278);

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

import javax.jws.WebParam;

import org.eclipse.core.resources.IMarker;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.core.runtime.OperationCanceledException;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jst.ws.annotations.core.AnnotationsCore;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.internal.jaxws.core.JAXWSCoreMessages;

public class WebServiceSEINoWebParamRuleTest extends AbstractWebServiceSEIRule {

    @Override
    protected Annotation getAnnotation() {
        return AnnotationsCore.createAnnotation(ast, WebParam.class, WebParam.class.getSimpleName(), null);
    }

    public void testWebServiceSEIPresentNoWebParamRule() {
        try {
            assertNotNull(annotation);
            assertEquals(WebParam.class.getSimpleName(), AnnotationUtils.getAnnotationName(annotation));

            IMethod method = source.findPrimaryType().getMethod("methodOne", new String[] { "QString;" });
            assertNotNull(method);

            AnnotationUtils.addImportChange(compilationUnit, WebParam.class, textFileChange, true);

            SingleVariableDeclaration parameter = AnnotationUtils.getMethodParameter(compilationUnit, method,
                    250);

            AnnotationUtils.createMethodParameterAnnotationChange(source, compilationUnit, rewriter,
                    parameter, method, annotation, textFileChange);

            assertTrue(executeChange(new NullProgressMonitor(), textFileChange));

            // refresh
            parameter = AnnotationUtils.getMethodParameter(AnnotationUtils.getASTParser(method
                    .getCompilationUnit()), method, 278);

            assertTrue(AnnotationUtils.isAnnotationPresent(parameter, annotation));
            
            Job.getJobManager().join(ResourcesPlugin.FAMILY_AUTO_BUILD, null);

            IMarker[] allmarkers = source.getResource().findMarkers(IMarker.PROBLEM, true,
                    IResource.DEPTH_INFINITE);

            assertEquals(1, allmarkers.length);

            IMarker annotationProblemMarker = allmarkers[0];

            assertEquals(source.getResource(), annotationProblemMarker.getResource());
            assertEquals(JAXWSCoreMessages.WEBSERVICE_ENPOINTINTERFACE_NO_WEBPARAM,
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