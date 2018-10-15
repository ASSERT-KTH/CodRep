return LongID.class.getName();

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.identity;

import org.eclipse.osgi.util.NLS;

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
			super(LongID.class.getName(), "LongID Namespace"); //$NON-NLS-1$
		}

		/**
		 * @param args
		 *            must not be <code>null></code>
		 * @return ID created. Will not be <code>null</code>.
		 * @throws IDCreateException
		 *             never thrown
		 */
		public ID createInstance(Object[] args) throws IDCreateException {
			try {
				String init = getInitStringFromExternalForm(args);
				if (init != null)
					return new LongID(this, Long.decode(init));
				return new LongID(this, (Long) args[0]);
			} catch (Exception e) {
				throw new IDCreateException(NLS.bind(
						"{0} createInstance()", getName()), e); //$NON-NLS-1$
			}
		}

		public String getScheme() {
			return LongID.class.toString();
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @seeorg.eclipse.ecf.core.identity.Namespace#
		 * getSupportedParameterTypesForCreateInstance()
		 */
		public Class[][] getSupportedParameterTypes() {
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

	public String toString() {
		StringBuffer sb = new StringBuffer("LongID["); //$NON-NLS-1$
		sb.append(value).append("]"); //$NON-NLS-1$
		return sb.toString();

	}
}
 No newline at end of file