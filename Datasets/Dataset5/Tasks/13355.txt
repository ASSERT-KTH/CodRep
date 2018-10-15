package org.eclipse.wst.xml.vex.core.internal.validator;

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
package org.eclipse.wst.xml.vex.core.internal.dom;

import java.io.ObjectStreamException;
import java.io.Serializable;

/**
 * <code>AttributeDefinition</code> represents an attribute definition in a DTD.
 * @model
 */
public class AttributeDefinition implements Comparable, Serializable {

	private String name;
	private Type type;
	private String defaultValue;
	private String[] values;
	private boolean required;
	private boolean fixed;

	/**
	 * Enumeration of attribute types.
	 * 
	 */
	public static final class Type implements Serializable {

		private String s;

		public static final Type CDATA = new Type("CDATA");
		public static final Type ID = new Type("ID");
		public static final Type IDREF = new Type("IDREF");
		public static final Type IDREFS = new Type("IDREFS");
		public static final Type NMTOKEN = new Type("NMTOKEN");
		public static final Type NMTOKENS = new Type("NMTOKENS");
		public static final Type ENTITY = new Type("ENTITY");
		public static final Type ENTITIES = new Type("ENTITIES");
		public static final Type NOTATION = new Type("NOTATION");
		public static final Type ENUMERATION = new Type("ENUMERATION");

		private Type(String s) {
			this.s = s;
		}

		public static Type get(String s) {
			if (s.equals(CDATA.toString())) {
				return CDATA;
			} else if (s.equals(ID.toString())) {
				return ID;
			} else if (s.equals(IDREF.toString())) {
				return IDREF;
			} else if (s.equals(IDREFS.toString())) {
				return IDREFS;
			} else if (s.equals(NMTOKEN.toString())) {
				return NMTOKEN;
			} else if (s.equals(NMTOKENS.toString())) {
				return NMTOKENS;
			} else if (s.equals(ENTITY.toString())) {
				return ENTITY;
			} else if (s.equals(ENTITIES.toString())) {
				return ENTITIES;
			} else if (s.equals(NOTATION.toString())) {
				return NOTATION;
			} else if (s.equals(ENUMERATION.toString())) {
				return ENUMERATION;
			} else {
				throw new IllegalArgumentException("Attribute type '" + s
						+ "' not recognized");
			}
		}

		public String toString() {
			return this.s;
		}

		/**
		 * Serialization method, to ensure that we do not introduce new
		 * instances.
		 */
		private Object readResolve() throws ObjectStreamException {
			return get(this.toString());
		}
	}

	/**
	 * Class constructor.
	 */
	public AttributeDefinition(String name, Type type, String defaultValue,
			String[] values, boolean required, boolean fixed) {

		this.name = name;
		this.type = type;
		this.defaultValue = defaultValue;
		this.values = values;
		this.required = required;
		this.fixed = fixed;
	}

	/**
	 * Implements <code>Comparable.compareTo</code> to sort alphabetically by
	 * name.
	 * 
	 * @param other
	 *            The attribute to which this one is to be compared.
	 *
	 */
	public int compareTo(Object other) {
		return this.name.compareTo(((AttributeDefinition) other).name);
	}

	/**
	 * Returns the attribute's type.
	 * @model
	 */
	public Type getType() {
		return this.type;
	}

	/**
	 * Returns the default value of the attribute.
	 * @model
	 */
	public String getDefaultValue() {
		return defaultValue;
	}

	/**
	 * Returns true if the attribute value is fixed.
	 * @model
	 */
	public boolean isFixed() {
		return fixed;
	}

	/**
	 * Returns the name of the attribute.
	 * @model
	 */
	public String getName() {
		return name;
	}

	/**
	 * Returns true if the attribute is required.
	 * @model
	 */
	public boolean isRequired() {
		return required;
	}

	/**
	 * Returns an array of acceptable values for the attribute. If null is
	 * returned, any value is acceptable for the attribute.
	 * @model type="String" containment="true"
	 */
	public String[] getValues() {
		return values;
	}

}