import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;

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
package org.eclipse.jst.ws.internal.cxf.facet;

import java.math.BigInteger;
import java.util.List;

import org.eclipse.core.resources.IProject;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.Path;
import org.eclipse.core.runtime.Status;
import org.eclipse.jdt.apt.core.util.AptConfig;
import org.eclipse.jdt.core.IAccessRule;
import org.eclipse.jdt.core.IClasspathAttribute;
import org.eclipse.jdt.core.IClasspathEntry;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jem.java.JavaClass;
import org.eclipse.jem.java.JavaRefFactory;
import org.eclipse.jst.j2ee.common.CommonFactory;
import org.eclipse.jst.j2ee.common.Listener;
import org.eclipse.jst.j2ee.model.IModelProvider;
import org.eclipse.jst.j2ee.model.ModelProviderManager;
import org.eclipse.jst.j2ee.webapplication.ContextParam;
import org.eclipse.jst.j2ee.webapplication.ServletType;
import org.eclipse.jst.j2ee.webapplication.WebapplicationFactory;
import org.eclipse.jst.javaee.core.Description;
import org.eclipse.jst.javaee.core.DisplayName;
import org.eclipse.jst.javaee.core.JavaeeFactory;
import org.eclipse.jst.javaee.core.ParamValue;
import org.eclipse.jst.javaee.core.UrlPatternType;
import org.eclipse.jst.javaee.web.Servlet;
import org.eclipse.jst.javaee.web.ServletMapping;
import org.eclipse.jst.javaee.web.SessionConfig;
import org.eclipse.jst.javaee.web.WebFactory;
import org.eclipse.jst.ws.internal.cxf.core.CXFCoreMessages;
import org.eclipse.jst.ws.internal.cxf.core.CXFCorePlugin;
import org.eclipse.jst.ws.internal.cxf.core.utils.JDTUtils;
import org.eclipse.wst.common.project.facet.core.IDelegate;
import org.eclipse.wst.common.project.facet.core.IProjectFacetVersion;

/**
 * Copies the contents of the cxf lib folder from the cxf home directory into
 * the WEB-INF/lib in the web projects WebContent directory.
 * <p>
 * Also sets up the web projects application deployment descriptor (web.xml file)
 * to use cxf-servlet or the Spring Application context (WEB-INF/beans.xml) for 
 * endpoint configuration. Depends on a setting in the CXF preferences. 
 * 
 * @author sclarke
 */
public class CXFFacetInstallDelegate implements IDelegate {

    public void execute(final IProject project, IProjectFacetVersion fv, Object config,
            IProgressMonitor monitor) throws CoreException {

        if (CXFCorePlugin.getDefault().getJava2WSContext().getCxfRuntimeLocation().equals("")) { //$NON-NLS-1$
            throw new CoreException(new Status(Status.ERROR, CXFCorePlugin.PLUGIN_ID,
                    CXFCoreMessages.CXF_FACET_INSTALL_DELEGATE_RUNTIME_LOCATION_NOT_SET));
        }

        IPath cxfLibPath = new Path(CXFCorePlugin.getDefault().getJava2WSContext().getCxfRuntimeLocation());
        if (!cxfLibPath.hasTrailingSeparator()) {
            cxfLibPath = cxfLibPath.addTrailingSeparator();
        }
        cxfLibPath = cxfLibPath.append("lib"); //$NON-NLS-1$

        IClasspathAttribute jstComponentDependency = 
            JavaCore.newClasspathAttribute("org.eclipse.jst.component.dependency", "/WEB-INF/lib"); //$NON-NLS-1$
        IClasspathEntry cxfClasspathContainer = 
            JavaCore.newContainerEntry(new Path("org.eclipse.jst.ws.cxf.core.CXF_CLASSPATH_CONTAINER"), //$NON-NLS-1$
            new IAccessRule[0],
            CXFCorePlugin.getDefault().getJava2WSContext().isExportCXFClasspathContainer() 
            ? new IClasspathAttribute[]{jstComponentDependency} : new IClasspathAttribute[]{},
            true);
        
        JDTUtils.addToClasspath(JavaCore.create(project), cxfClasspathContainer);
        
        // Add CXF Servlet, Servlet Mapping and Session Config to web.xml
        final IModelProvider provider = ModelProviderManager.getModelProvider(project);
        provider.modify(new Runnable() {
            public void run() {
                Object modelProvider = provider.getModelObject();
                boolean useSpringAppContext = CXFCorePlugin.getDefault().getJava2WSContext()
                        .isUseSpringApplicationContext();
                // jst.web 2.5
                if (modelProvider instanceof org.eclipse.jst.javaee.web.WebApp) {
                    org.eclipse.jst.javaee.web.WebApp javaeeWebApp = 
                        (org.eclipse.jst.javaee.web.WebApp) modelProvider;
                    addCXFJSTWEB25Servlet(project, javaeeWebApp);
                    if (useSpringAppContext) {
                        addSpringApplicationContextWeb25(project, javaeeWebApp);
                    }
                }
                // jst.web 2.4
                if (modelProvider instanceof org.eclipse.jst.j2ee.webapplication.WebApp) {
                    org.eclipse.jst.j2ee.webapplication.WebApp webApp = 
                        (org.eclipse.jst.j2ee.webapplication.WebApp) modelProvider;
                    addCXFJSTWEB24Servlet(project, webApp);
                    if (useSpringAppContext) {
                        addSpringApplicationContextWeb24(project, webApp);
                    }
                }
            }
        }, null);

        if (CXFCorePlugin.getDefault().getJava2WSContext().isAnnotationProcessingEnabled()) {
            AptConfig.setEnabled(JavaCore.create(project), true);    
        }
    }

    @SuppressWarnings("unchecked")
    private void addSpringApplicationContextWeb24(IProject webProject,
            org.eclipse.jst.j2ee.webapplication.WebApp webapp) {
        List contextParams = webapp.getContextParams();
        for (int i = 0; i < contextParams.size(); i++) {
            ContextParam contextParam = (ContextParam) contextParams.get(i);
            if (contextParam.getParamName().equals("contextConfigLocation")) { //$NON-NLS-1$
                return;
            }
        }
        // org.eclipse.jst.javaee.core.ParamValue
        List listeners = webapp.getListeners();
        for (int i = 0; i < listeners.size(); i++) {
            Listener contextLoaderListener = (Listener) listeners.get(i);
            if (contextLoaderListener.getListenerClass().getName().equals(
                    "org.springframework.web.context.ContextLoaderListener")) { //$NON-NLS-1$
                return;
            }
        }

        CommonFactory commonFactory = CommonFactory.eINSTANCE;
        JavaRefFactory javaRefFactory = JavaRefFactory.eINSTANCE;

        org.eclipse.jst.j2ee.common.ParamValue configLocationParam = commonFactory.createParamValue();
        configLocationParam.setName("contextConfigLocation"); //$NON-NLS-1$
        configLocationParam.setValue("WEB-INF/beans.xml"); //$NON-NLS-1$

        webapp.getContextParams().add(configLocationParam);

        Listener contextLoaderListener = commonFactory.createListener();
        JavaClass javaClass = javaRefFactory.createJavaClass();
        javaClass.setName("org.springframework.web.context.ContextLoaderListener"); //$NON-NLS-1$
        contextLoaderListener.setListenerClass(javaClass);

        webapp.getListeners().add(contextLoaderListener);
    }

    @SuppressWarnings("unchecked")
    private void addSpringApplicationContextWeb25(IProject webProject,
            org.eclipse.jst.javaee.web.WebApp webapp) {
        List contextParams = webapp.getContextParams();
        for (int i = 0; i < contextParams.size(); i++) {
            ParamValue contextParam = (ParamValue) contextParams.get(i);
            if (contextParam.getParamName().equals("contextConfigLocation")) { //$NON-NLS-1$
                return;
            }
        }

        List listeners = webapp.getListeners();
        for (int i = 0; i < listeners.size(); i++) {
            org.eclipse.jst.javaee.core.Listener contextLoaderListener = (org.eclipse.jst.javaee.core.Listener) listeners
                    .get(i);
            if (contextLoaderListener.getListenerClass().equals(
                    "org.springframework.web.context.ContextLoaderListener")) { //$NON-NLS-1$
                return;
            }
        }

        JavaeeFactory javaeeFactory = JavaeeFactory.eINSTANCE;

        ParamValue configLocationParam = javaeeFactory.createParamValue();
        configLocationParam.setParamName("contextConfigLocation"); //$NON-NLS-1$
        configLocationParam.setParamValue("WEB-INF/beans.xml"); //$NON-NLS-1$

        webapp.getContextParams().add(configLocationParam);

        org.eclipse.jst.javaee.core.Listener contextLoaderListener = javaeeFactory.createListener();
        contextLoaderListener.setListenerClass("org.springframework.web.context.ContextLoaderListener"); //$NON-NLS-1$

        webapp.getListeners().add(contextLoaderListener);
    }

    @SuppressWarnings("unchecked")
    private void addCXFJSTWEB24Servlet(IProject webProject, org.eclipse.jst.j2ee.webapplication.WebApp webapp) {
        List servlets = webapp.getServlets();
        for (int i = 0; i < servlets.size(); i++) {
            Servlet servlet = (Servlet) servlets.get(i);
            if (servlet.getServletName().equals("cxf")) { //$NON-NLS-1$
                return;
            }
        }

        WebapplicationFactory factory = WebapplicationFactory.eINSTANCE;

        org.eclipse.jst.j2ee.webapplication.Servlet cxfServlet = factory.createServlet();
        ServletType servletType = factory.createServletType();
        cxfServlet.setWebType(servletType);
        cxfServlet.setServletName("cxf"); //$NON-NLS-1$
        servletType.setClassName("org.apache.cxf.transport.servlet.CXFServlet"); //$NON-NLS-1$
        cxfServlet.setDisplayName("cxf"); //$NON-NLS-1$
        cxfServlet.setLoadOnStartup(Integer.valueOf(1));

        webapp.getServlets().add(cxfServlet);

        org.eclipse.jst.j2ee.webapplication.ServletMapping servletMapping = factory.createServletMapping();
        servletMapping.setServlet(cxfServlet);
        servletMapping.setUrlPattern("/services/*"); //$NON-NLS-1$
        webapp.getServletMappings().add(servletMapping);

        org.eclipse.jst.j2ee.webapplication.SessionConfig sessionConfig = factory.createSessionConfig();
        sessionConfig.setSessionTimeout(60);
        webapp.setSessionConfig(sessionConfig);
    }

    @SuppressWarnings("unchecked")
    private void addCXFJSTWEB25Servlet(IProject webProject, org.eclipse.jst.javaee.web.WebApp webapp) {
        List servlets = webapp.getServlets();
        for (int i = 0; i < servlets.size(); i++) {
            Servlet servlet = (Servlet) servlets.get(i);
            if (servlet.getServletName().equals("cxf")) { //$NON-NLS-1$
                return;
            }
        }

        // CXF Servlet
        WebFactory factory = WebFactory.eINSTANCE;
        Servlet cxfServlet = factory.createServlet();

        cxfServlet.setServletName("cxf"); //$NON-NLS-1$

        DisplayName cxfServletDisplayName = JavaeeFactory.eINSTANCE.createDisplayName();
        cxfServletDisplayName.setValue("cxf"); //$NON-NLS-1$
        cxfServlet.getDisplayNames().add(cxfServletDisplayName);

        Description cxfServletDescription = JavaeeFactory.eINSTANCE.createDescription();
        cxfServletDescription.setValue("Apache CXF Endpoint"); //$NON-NLS-1$
        cxfServlet.getDescriptions().add(cxfServletDescription);

        cxfServlet.setServletClass("org.apache.cxf.transport.servlet.CXFServlet"); //$NON-NLS-1$

        cxfServlet.setLoadOnStartup(Integer.valueOf(1));

        webapp.getServlets().add(cxfServlet);

        ServletMapping cxfServletMapping = factory.createServletMapping();
        cxfServletMapping.setServletName("cxf"); //$NON-NLS-1$
        UrlPatternType url = JavaeeFactory.eINSTANCE.createUrlPatternType();
        url.setValue("/services/*"); //$NON-NLS-1$
        cxfServletMapping.getUrlPatterns().add(url);
        webapp.getServletMappings().add(cxfServletMapping);

        SessionConfig sessionConfig = factory.createSessionConfig();
        sessionConfig.setSessionTimeout(new BigInteger("60")); //$NON-NLS-1$
        webapp.getSessionConfigs().add(sessionConfig);
    }
}