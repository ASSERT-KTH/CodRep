if (!ClasspathUriResolver.isClasspathUri(iconNormalizedURI) && checkAccessable(iconNormalizedURI))

package org.eclipse.emf.editor.provider;

/**
 * <copyright> 
 *
 * Copyright (c) 2008 itemis AG and others.
 * All rights reserved.   This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: 
 *   itemis AG - Initial API and implementation
 *
 * </copyright>
 *
 */

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.net.MalformedURLException;
import java.net.URL;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.Path;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.edit.provider.IItemLabelProvider;
import org.eclipse.emf.editor.EEPlugin;
import org.eclipse.emf.editor.extxpt.ExtXptFacade;
import org.eclipse.emf.editor.ui.ImageRegistry;

/**
 * @author Dennis Huebner
 * 
 */
public class ExtendedLabelProvider implements IItemLabelProvider {

	private static final String ICONS_FOLDER = "icons";
	private static final String ICON_EXTENSION_NAME = "icon";
	private static final String LABEL_EXTENSION_NAME = "label";
	private final ExtXptFacade facade;
	private IItemLabelProvider registryItemLabelProvider;

	public ExtendedLabelProvider(ExtXptFacade facade) {
		this.facade = facade;
		this.registryItemLabelProvider = new RegistryItemLabelProvider();
	}

	public Object getImage(Object element) {
		Object retVal = null;
		try {
			if (element instanceof EObject) {
				EObject eObject = (EObject) element;
				String iconName = evaluate(eObject, ICON_EXTENSION_NAME);
				if (iconName != null) {
					// TODO try instance scope
					retVal = locateImage(iconName, eObject.eResource(), eObject);
					// if not found try metamodel scope
					Resource eResource = eObject.eClass().eResource();
					if (retVal == null)
						retVal = locateImage(iconName, eResource, eObject);
				}
			}
		}
		catch (Throwable ex) {
			EEPlugin.logError("ERROR fetching Icon", ex);
		}
		if (retVal == null) {
			// Fallback: Ask registry for image
			retVal = registryItemLabelProvider.getImage(element);
		}
		return retVal;

	}

	/**
	 * @param iconName
	 * @param eResource
	 * @param eObject
	 * @return
	 * @throws MalformedURLException
	 * @throws IOException
	 */
	private Object locateImage(String iconName, Resource eResource, EObject eObject) throws MalformedURLException,
			IOException {
		// TODO understand the requirements :)
		Object retVal = null;
		if (eResource != null) {
			URI metaModelURI = eResource.getURI();
			URI iconURI = createIconURI(eObject, iconName, metaModelURI);

			if (metaModelURI.isPlatform()) {
				// platform resource... good
				String platformString = metaModelURI.toPlatformString(true);

				IFile metaModelFile = ResourcesPlugin.getWorkspace().getRoot().getFile(new Path(platformString));
				if (metaModelFile != null) {
					// using IFile to allow resource change listening
					IFile f = metaModelFile.getProject().getFile(iconURI.path());
					if (f != null && f.exists()) {
						// ask registry
						retVal = ImageRegistry.getDefault().getImage(f);
					}
				}
			}
			else if (metaModelURI.isArchive()) {// archived
				// handle archived resources
				// return URI. Image will be stored in
				// ExtendedImageRegistry
				// which is not refreshable
				if (checkAccessable(iconURI))
					retVal = iconURI;
			}
			else {
				// eResource not present physically... bad
				URI classpathURI = URI.createURI(ClasspathUriResolver.CLASSPATH_SCHEME + ":" + iconURI.path());
				URI iconNormalizedURI = new ClasspathUriResolver().resolve(facade.getProject(), classpathURI);
				// return URI. Image will be stored in
				// ExtendedImageRegistry
				// which is not refreshable
				if (!ClasspathUriResolver.isClassapthUri(iconNormalizedURI) && checkAccessable(iconNormalizedURI))
					retVal = iconNormalizedURI;
			}
		}
		return retVal;
	}

	private boolean checkAccessable(URI iconURI) throws IOException {
		URL url = new URL(iconURI.toString());
		if (url != null) {
			try {
				InputStream in = url.openStream();// check readable
				in.close();
				return true;
			}
			catch (FileNotFoundException e) {
				// ignore no feedback to user
			}
		}
		return false;
	}

	/**
	 * @param element
	 * @param iconName
	 * @param metaModelURI
	 * @return
	 */
	private URI createIconURI(EObject eObject, String iconName, URI metaModelURI) {
		String packageName = packageName(eObject);
		return metaModelURI.trimSegments(metaModelURI.segmentCount()).appendSegment(ICONS_FOLDER).appendSegment(
				packageName).appendSegment(iconName);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.emf.edit.provider.IItemLabelProvider#getText(java.lang.Object
	 * )
	 */
	public String getText(Object element) {
		String text = evaluate(element, LABEL_EXTENSION_NAME);
		return text;
	}

	/**
	 * @param element
	 * @param retVal
	 * @return
	 */
	private String evaluate(Object element, String name) {
		String retVal = null;
		if (element instanceof EObject && facade != null) {
			EObject eO = (EObject) element;
			retVal = (String) facade.style(name, eO);
		}
		return retVal;
	}

	/**
	 * @param object
	 * @return
	 */
	private String packageName(EObject object) {
		return object.eClass().getEPackage().getName();
	}

}