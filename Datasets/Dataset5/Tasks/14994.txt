if (ws.getImplementation()!= null && ws.getImplementation().equals(implName))

/*******************************************************************************
 * Copyright (c) 2009 by SAP AG, Walldorf. 
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     SAP AG - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.jaxws.dom.runtime.persistence.sync;

import static org.eclipse.jst.ws.jaxws.dom.runtime.persistence.WSAnnotationFeatures.ENDPOINT_INTERFACE_ATTRIBUTE;
import static org.eclipse.jst.ws.jaxws.dom.runtime.persistence.WSAnnotationFeatures.PORT_NAME_ATTRIBUTE;
import static org.eclipse.jst.ws.jaxws.dom.runtime.persistence.WSAnnotationFeatures.SERVICE_NAME_ATTRIBUTE;
import static org.eclipse.jst.ws.jaxws.dom.runtime.persistence.WSAnnotationFeatures.TARGET_NAMESPACE_ATTRIBUTE;
import static org.eclipse.jst.ws.jaxws.dom.runtime.persistence.WSAnnotationFeatures.WSDL_LOCATION_ATTRIBUTE;
import static org.eclipse.jst.ws.jaxws.dom.runtime.persistence.WSAnnotationFeatures.WS_ANNOTATION;

import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jst.ws.jaxws.dom.runtime.api.DomFactory;
import org.eclipse.jst.ws.jaxws.dom.runtime.api.DomPackage;
import org.eclipse.jst.ws.jaxws.dom.runtime.api.IServiceEndpointInterface;
import org.eclipse.jst.ws.jaxws.dom.runtime.api.IWebService;
import org.eclipse.jst.ws.jaxws.dom.runtime.api.IWebServiceProject;
import org.eclipse.jst.ws.jaxws.dom.runtime.persistence.IAnnotationSerializer;
import org.eclipse.jst.ws.jaxws.dom.runtime.persistence.IModelElementSynchronizer;
import org.eclipse.jst.ws.jaxws.utils.JaxWsUtils;
import org.eclipse.jst.ws.jaxws.utils.annotations.IAnnotation;
import org.eclipse.jst.ws.jaxws.utils.annotations.IAnnotationInspector;

public class WsSynchronizer extends ElementSynchronizerImpl
{
	private final SeiMerger seiMerger;

	public WsSynchronizer(IModelElementSynchronizer parent)
	{
		super(parent);
		this.seiMerger = new SeiMerger(this, new WSMethodSynchronizer(this));
	}

	private IWebService obtainInstance(IWebServiceProject wsProject, String implName)
	{
		for (IWebService ws : wsProject.getWebServices())
		{
			if (ws.getImplementation().equals(implName))
			{
				return ws;
			}
		}
		final IWebService newWs = DomFactory.eINSTANCE.createIWebService();
		util().setFeatureValue(newWs, DomPackage.IJAVA_WEB_SERVICE_ELEMENT__IMPLEMENTATION, implName);
		util().addToCollectionFeature(wsProject, DomPackage.IWEB_SERVICE_PROJECT__WEB_SERVICES, newWs);
		
		return newWs;
	}

	public IWebService synchronizeWebService(IWebServiceProject wsProject, IAnnotation<IType> wsAnnotation, IAnnotationInspector inspector) throws JavaModelException
	{
		final IWebService ws = obtainInstance(wsProject, wsAnnotation.getAppliedElement().getFullyQualifiedName());
		mergeWebService(ws, wsProject, wsAnnotation, inspector);
		
		resource().getSerializerFactory().adapt(ws, IAnnotationSerializer.class);
		adaptToLocationInterface(ws, WS_ANNOTATION, wsAnnotation);
		
		return ws;
	}

	private void mergeWebService(IWebService toMerge, IWebServiceProject wsProject, IAnnotation<IType> wsAnnotation, IAnnotationInspector inspector) throws JavaModelException
	{
		// add serviceName name
		final String wsName = wsAnnotation.getPropertyValue(SERVICE_NAME_ATTRIBUTE) == null ?
				JaxWsUtils.getDefaultServiceName(wsAnnotation.getAppliedElement().getFullyQualifiedName()) : 
				wsAnnotation.getPropertyValue(SERVICE_NAME_ATTRIBUTE);
				
		if (!wsName.equals(toMerge.getName()))
		{
			util().setFeatureValue(toMerge, DomPackage.IWEB_SERVICE__NAME, wsName);
		}
		
		// add targetNamespace
		final String targetNs = extractTargetNamespace(wsAnnotation);
		if (!targetNs.equals(toMerge.getTargetNamespace())) {
			util().setFeatureValue(toMerge, DomPackage.IWEB_SERVICE__TARGET_NAMESPACE, targetNs);
		}
		
		// add portName
		final String portName = wsAnnotation.getPropertyValue(PORT_NAME_ATTRIBUTE)==null ?
				JaxWsUtils.getDefaultPortName(wsAnnotation.getAppliedElement().getFullyQualifiedName()) :
				wsAnnotation.getPropertyValue(PORT_NAME_ATTRIBUTE);
				
		if (!portName.equals(toMerge.getPortName())) {
			toMerge.setPortName(portName);
		}
		
		// add wsdlLocation
		toMerge.setWsdlLocation(wsAnnotation.getPropertyValue(WSDL_LOCATION_ATTRIBUTE));
		
		// add endpointInterface
		final String newSeiImpl = wsAnnotation.getPropertyValue(ENDPOINT_INTERFACE_ATTRIBUTE);
		if (newSeiImpl == null)
		{
			mergeImplicitInterface(obtainImplicitInterfaceInstance(wsProject, toMerge, wsAnnotation), wsAnnotation, inspector);
		} else
		{
			if (toMerge.getServiceEndpoint() == null || !toMerge.getServiceEndpoint().getImplementation().equals(newSeiImpl))
			{
				serviceData().map(toMerge, newSeiImpl);
				resolveInterface(toMerge, wsProject, wsAnnotation.getPropertyValue(ENDPOINT_INTERFACE_ATTRIBUTE));
			}
		}
	}

	private IServiceEndpointInterface obtainImplicitInterfaceInstance(IWebServiceProject wsProject, IWebService ws, IAnnotation<IType> wsAnnotation)
	{
		if (ws.getServiceEndpoint() != null && ws.getServiceEndpoint().isImplicit())
		{
			return ws.getServiceEndpoint();
		}

		final IServiceEndpointInterface sei = DomFactory.eINSTANCE.createIServiceEndpointInterface();
		util().setFeatureValue(sei, DomPackage.ISERVICE_ENDPOINT_INTERFACE__IMPLICIT, true);
		util().setFeatureValue(sei, DomPackage.IJAVA_WEB_SERVICE_ELEMENT__IMPLEMENTATION, wsAnnotation.getAppliedElement().getFullyQualifiedName());
		util().setFeatureValue(ws, DomPackage.IWEB_SERVICE__SERVICE_ENDPOINT, sei);
		
		wsProject.getServiceEndpointInterfaces().add(sei);
		
		return sei;
	}

	private void mergeImplicitInterface(IServiceEndpointInterface sei, IAnnotation<IType> wsAnnotation, IAnnotationInspector inspector) throws JavaModelException
	{
		seiMerger.merge(sei, wsAnnotation, inspector);
		resource().getSerializerFactory().adapt(sei, IAnnotationSerializer.class);
	}
	
	private String extractTargetNamespace(final IAnnotation<IType> wsAnnotation)
	{
		// add targetNamespace
		final String targetNs = wsAnnotation.getPropertyValue(TARGET_NAMESPACE_ATTRIBUTE);
		if (targetNs==null) {
			return JaxWsUtils.composeJaxWsTargetNamespaceByPackage(wsAnnotation.getAppliedElement().getPackageFragment().getElementName());
		}	
		
		return targetNs;
	}

	private void resolveInterface(IWebService ws, IWebServiceProject preffered, String implementation)
	{
		IServiceEndpointInterface resolved = null;
		for (IWebServiceProject prj : getDomBeingLoaded().getWebServiceProjects())
		{
			for (IServiceEndpointInterface sei : prj.getServiceEndpointInterfaces())
			{
				if (sei.getImplementation().equals(implementation))
				{
					resolved = sei;
					if (preffered.equals(prj))
					{
						break;
					} else
					{
						resolved = sei;
					}
				}
			}
		}

		util().setFeatureValue(ws, DomPackage.IWEB_SERVICE__SERVICE_ENDPOINT, resolved);
	}
}