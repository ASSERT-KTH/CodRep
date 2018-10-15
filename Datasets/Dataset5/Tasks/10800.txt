public Class[][] getSupportedParameterTypes() {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.identity;

/**
 * A unique ID class based upon Long/long
 * 
 */
public class LongID extends BaseID {
	private static final long serialVersionUID = 4049072748317914423L;

	Long value = null;

	public static class LongNamespace extends Namespace {
		private static final long serialVersionUID = -1580533392719331665L;

		public LongNamespace() {
			super(LongID.class.getName(), "Long Namespace");
		}

		public ID createInstance(Object[] args) throws IDCreateException {
			return new LongID(this, (Long) args[0]);
		}

		public String getScheme() {
			return LongID.class.toString();
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.core.identity.Namespace#getSupportedParameterTypesForCreateInstance()
		 */
		public Class[][] getSupportedParameterTypesForCreateInstance() {
			return new Class[][] { { Long.class } };
		}
	}

	protected LongID(Namespace n, Long v) {
		super(n);
		value = v;
	}

	protected LongID(Namespace n, long v) {
		super(n);
		value = new Long(v);
	}

	protected int namespaceCompareTo(BaseID o) {
		Long ovalue = ((LongID) o).value;
		return value.compareTo(ovalue);
	}

	protected boolean namespaceEquals(BaseID o) {
		if (!(o instanceof LongID))
			return false;
		LongID obj = (LongID) o;
		return value.equals(obj.value);
	}

	protected String namespaceGetName() {
		return value.toString();
	}

	protected int namespaceHashCode() {
		return value.hashCode();
	}

	public long longValue() {
		return value.longValue();
	}

}
 No newline at end of file