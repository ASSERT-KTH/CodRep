import org.eclipse.wst.xml.vex.core.internal.validator.DTDValidator;

/*******************************************************************************
 * Copyright (c) 2004, 2008 John Krasnay and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     John Krasnay - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.vex.ui.internal.config;

import java.io.IOException;
import java.net.URL;

import org.eclipse.wst.xml.vex.core.internal.dom.DTDValidator;

import com.wutka.dtd.DTDParseException;

/**
 * Factory for DocumentType objects.
 */
public class DoctypeFactory implements IConfigItemFactory {

	public IConfigElement[] createConfigurationElements(ConfigItem item) {
		DocumentType doctype = (DocumentType) item;
		ConfigurationElement doctypeElement = new ConfigurationElement(
				ELT_DOCTYPE);
		doctypeElement.setAttribute(ATTR_PUBLIC_ID, doctype.getPublicId());
		doctypeElement.setAttribute(ATTR_SYSTEM_ID, doctype.getSystemId());
		doctypeElement.setAttribute(ATTR_DTD, doctype.getResourcePath());
		doctypeElement.setAttribute(ATTR_OUTLINE_PROVIDER, doctype
				.getOutlineProvider());

		String[] names = doctype.getRootElements();
		for (int i = 0; i < names.length; i++) {
			String name = names[i];
			ConfigurationElement rootElement = new ConfigurationElement(
					ELT_ROOT_ELEMENT);
			rootElement.setAttribute(ATTR_NAME, name);
			doctypeElement.addChild(rootElement);
		}

		return new IConfigElement[] { doctypeElement };
	}

	public ConfigItem createItem(ConfigSource config,
			IConfigElement[] configElements) throws IOException {
		if (configElements.length < 1) {
			return null;
		}
		IConfigElement configElement = configElements[0];
		DocumentType doctype = new DocumentType(config);
		doctype.setPublicId(configElement.getAttribute(ATTR_PUBLIC_ID));
		doctype.setSystemId(configElement.getAttribute(ATTR_SYSTEM_ID));
		doctype.setResourcePath(configElement.getAttribute(ATTR_DTD));
		doctype.setOutlineProvider(configElement
				.getAttribute(ATTR_OUTLINE_PROVIDER));

		IConfigElement[] rootElementRefs = configElement.getChildren();
		String[] rootElements = new String[rootElementRefs.length];
		for (int i = 0; i < rootElementRefs.length; i++) {
			rootElements[i] = rootElementRefs[i].getAttribute("name"); //$NON-NLS-1$
		}
		doctype.setRootElements(rootElements);

		return doctype;
	}

	public String getExtensionPointId() {
		return DocumentType.EXTENSION_POINT;
	}

	public String[] getFileExtensions() {
		return EXTS;
	}

	public String getPluralName() {
		return Messages.getString("DoctypeFactory.pluralName"); //$NON-NLS-1$
	}

	public Object parseResource(URL baseUrl, String resourcePath,
			IBuildProblemHandler problemHandler) throws IOException {
		try {
			return DTDValidator.create(new URL(baseUrl, resourcePath));
		} catch (DTDParseException ex) {
			if (problemHandler != null) {
				BuildProblem problem = new BuildProblem();
				problem.setSeverity(BuildProblem.SEVERITY_ERROR);
				problem.setResourcePath(resourcePath);
				problem.setMessage(ex.getMessage());
				problem.setLineNumber(ex.getLineNumber());
				problemHandler.foundProblem(problem);
			}
			throw ex;
		}
	}

	// =================================================== PRIVATE

	private static final String[] EXTS = new String[] { "dtd" }; //$NON-NLS-1$

	private static final String ELT_DOCTYPE = "doctype"; //$NON-NLS-1$
	private static final String ATTR_OUTLINE_PROVIDER = "outlineProvider"; //$NON-NLS-1$
	private static final String ATTR_DTD = "dtd"; //$NON-NLS-1$
	private static final String ATTR_SYSTEM_ID = "systemId"; //$NON-NLS-1$
	private static final String ATTR_PUBLIC_ID = "publicId"; //$NON-NLS-1$

	private static final String ELT_ROOT_ELEMENT = "rootElement"; //$NON-NLS-1$
	private static final String ATTR_NAME = "name"; //$NON-NLS-1$

}