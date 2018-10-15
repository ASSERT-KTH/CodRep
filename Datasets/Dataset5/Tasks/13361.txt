import org.eclipse.wst.xml.vex.core.internal.provisional.dom.IValidator;

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

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.eclipse.wst.xml.vex.core.internal.dom.IValidator;
import org.eclipse.wst.xml.vex.ui.internal.editor.VexEditor;

/**
 * A registered document type.
 */
public class DocumentType extends ConfigItem implements Comparable {

	public static final String EXTENSION_POINT = "org.eclipse.wst.xml.vex.ui.doctypes"; //$NON-NLS-1$

	public DocumentType(ConfigSource config) {
		super(config);
	}

	/**
	 * Return a DocumentType for the given publicId. Returns null if no document
	 * type was found that matches the public ID.
	 * 
	 * @param publicId
	 *            Public ID for which to search.
	 */
	public static DocumentType getDocumentType(String publicId) {
		ConfigRegistry registry = ConfigRegistry.getInstance();
		List doctypes = registry
				.getAllConfigItems(DocumentType.EXTENSION_POINT);
		for (Iterator it = doctypes.iterator(); it.hasNext();) {
			DocumentType doctype = (DocumentType) it.next();
			if (doctype.getPublicId().equals(publicId)) {
				return doctype;
			}
		}
		return null;
	}

	/**
	 * Return a list of document types for which there is at least one
	 * registered style.
	 */
	public static DocumentType[] getDocumentTypesWithStyles() {
		// TODO quite inefficent, try caching results, clearing the cache upon
		// config changes.
		ConfigRegistry registry = ConfigRegistry.getInstance();
		List withStyles = new ArrayList();
		List doctypes = registry
				.getAllConfigItems(DocumentType.EXTENSION_POINT);
		for (Iterator it = doctypes.iterator(); it.hasNext();) {
			DocumentType doctype = (DocumentType) it.next();
			if (VexEditor.findStyleForDoctype(doctype.getPublicId()) != null) {
				withStyles.add(doctype);
			}
		}
		return (DocumentType[]) withStyles.toArray(new DocumentType[withStyles
				.size()]);
	}

	/**
	 * Returns the name of the class that generates an outline for this document
	 * type. This class must implement
	 * org.eclipse.ui.views.contentoutline.IContentOutlinePage. Normally,
	 * classes will extend
	 * org.eclipse.wst.vex.ui.internal.editor.AbstractContentOutlinePage.
	 * Returns null if this document type was not supplied by a plugin, or if
	 * the the contentOutlinePage attribute was not set.
	 */
	public String getOutlineProvider() {
		return outlineProvider;
	}

	/**
	 * Returns the public ID of the document type.
	 */
	public String getPublicId() {
		return publicId;
	}

	/**
	 * Returns the system ID of the document type.
	 */
	public String getSystemId() {
		return systemId;
	}

	public String getExtensionPointId() {
		return EXTENSION_POINT;
	}

	/**
	 * Sets the name of the class that defines the content outline of the
	 * document.
	 * 
	 * @param contentOutlinePage
	 *            Name of a class implementing IContentOutlinePage.
	 */
	public void setOutlineProvider(String contentOutlinePage) {
		this.outlineProvider = contentOutlinePage;
	}

	/**
	 * Sets the public ID of the document type. The public ID is the unique
	 * identifier of the document type.
	 * 
	 * @param publicId
	 *            new public ID of the document type.
	 */
	public void setPublicId(String publicId) {
		this.publicId = publicId;
	}

	/**
	 * Sets the system ID of the document type. This is used when creating new
	 * documents but ignored otherwise.
	 * 
	 * @param systemId
	 *            new system ID for the document type.
	 */
	public void setSystemId(String systemId) {
		this.systemId = systemId;
	}

	public IValidator getValidator() {
		return (IValidator) this.getConfig().getParsedResource(
				this.getResourcePath());
	}

	public boolean isValid() {
		return super.isValid() && !isBlank(publicId) && !isBlank(systemId)
				&& this.getValidator() != null;
	}

	public String toString() {
		return this.getName();
	}

	/**
	 * Returns a list of valid root elements for this document type. If no root
	 * elements have been declared, returns an empty array.
	 */
	public String[] getRootElements() {
		return rootElements;
	}

	/**
	 * Sets the list of valid root elements for this document type.
	 */
	public void setRootElements(String[] rootElements) {
		if (rootElements == null) {
			throw new IllegalArgumentException();
		}
		this.rootElements = rootElements;
	}

	// ==================================================== PRIVATE

	private static final String[] EMPTY_STRING_ARRAY = new String[0];

	private String publicId;
	private String systemId;
	private String outlineProvider;
	private String[] rootElements = EMPTY_STRING_ARRAY;

}