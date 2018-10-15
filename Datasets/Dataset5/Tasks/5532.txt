public List<AttributeDefinition> getAttributeDefinitions(String element);

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
package org.eclipse.wst.xml.vex.core.internal.provisional.dom;

import java.io.Serializable;
import java.util.Set;
import java.util.List;

import org.eclipse.wst.xml.vex.core.internal.validator.AttributeDefinition;

/**
 * Represents an object that can validate the structure of a document.
 * Validators must be serializable.
 * @model
 */
public interface Validator extends Serializable {

	/**
	 * String indicating that character data is allowed at the given point in
	 * the document.
	 * @model
	 */
	public static final String PCDATA = "#PCDATA";

	/**
	 * Returns the AttributeDefinition for a particular attribute.
	 * 
	 * @param element
	 *            Name of the element.
	 * @param attribute
	 *            Name of the attribute.
	 * @model
	 */
	public AttributeDefinition getAttributeDefinition(String element,
			String attribute);

	/**
	 * Returns the attribute definitions that apply to the given element.
	 * 
	 * @param element
	 *            Name of the element to check.
	 * @model
	 */
	public AttributeDefinition[] getAttributeDefinitions(String element);

	/**
	 * Returns a set of Strings representing valid root elements for the given
	 * document type.
	 * @model 
	 */
	public Set getValidRootElements();

	/**
	 * Returns a set of Strings representing items that are valid at point in
	 * the child nodes of a given element. Each string is either an element name
	 * or Validator.PCDATA.
	 * 
	 * @param element
	 *            Name of the parent element.
	 * @model 
	 */
	public Set<String> getValidItems(String element);

	/**
	 * Returns true if the given sequence is valid for the given element.
	 * Accepts three sequences, which will be concatenated before doing the
	 * check.
	 * 
	 * @param element
	 *            Name of the element being tested.
	 * @param nodes
	 *            Array of element names and Validator.PCDATA.
	 * @param partial
	 *            If true, an valid but incomplete sequence is acceptable.
	 * @model
	 */
	public boolean isValidSequence(String element, List<String> nodes,
			boolean partial);

	/**
	 * Returns true if the given sequence is valid for the given element.
	 * Accepts three sequences, which will be concatenated before doing the
	 * check.
	 * 
	 * @param element
	 *            Name of the element being tested.
	 * @param seq1
	 *            List of element names and Validator.PCDATA.
	 * @param seq2
	 *            List of element names and Validator.PCDATA. May be null or
	 *            empty.
	 * @param seq3
	 *            List of element names and Validator.PCDATA. May be null or
	 *            empty.
	 * @param partial
	 *            If true, an valid but incomplete sequence is acceptable.
	 * @model
	 */
	public boolean isValidSequence(String element, List<String> seq1,
			List<String> seq2, List<String> seq3, boolean partial);

}