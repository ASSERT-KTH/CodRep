private static final String LINK_PREFIX = "http://help.eclipse.org/stable/nftopic/org.eclipse.platform.doc.isv/reference/api/"; //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2007 Remy Suen and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.presence.bot.kosmos;

import java.util.Map;

class Javadoc {

	private static final String LINK_PREFIX = "http://help.eclipse.org/help32/nftopic/org.eclipse.platform.doc.isv/reference/api/"; //$NON-NLS-1$
	private static final String LINK_SUFFIX = ".html"; //$NON-NLS-1$

	private Map javadocs;
	private String fqn;
	private String link;

	Javadoc(Map javadocs, String fullQualifiedName) {
		this.javadocs = javadocs;
		fqn = fullQualifiedName;
		link = LINK_PREFIX + fqn.replaceAll("\\.", "/") + LINK_SUFFIX; //$NON-NLS-1$ //$NON-NLS-2$
	}

	String getField(String field) {
		return link + '#' + field;
	}

	String getMethod(String methodName, String[] array) {
		String ret = link + '#' + methodName + '(';
		for (int i = 0; i < array.length; i++) {
			Object match = javadocs.get(array[i]);
			if (match == null) {
				if (array[i].equals("int") || array[i].equals("float") //$NON-NLS-1$ //$NON-NLS-2$
						|| array[i].equals("short") || array[i].equals("long") //$NON-NLS-1$ //$NON-NLS-2$
						|| array[i].equals("byte") //$NON-NLS-1$
						|| array[i].equals("boolean") //$NON-NLS-1$
						|| array[i].equals("double") || array[i].equals("char")) { //$NON-NLS-1$ //$NON-NLS-2$
					ret = ret + array[i] + ",%20"; //$NON-NLS-1$
				} else if (array[i].equals("Object") //$NON-NLS-1$
						|| array[i].equals("Class") //$NON-NLS-1$
						|| array[i].equals("String")) { //$NON-NLS-1$
					ret = ret + "java.lang." + array[i] + ",%20"; //$NON-NLS-1$ //$NON-NLS-2$
				} else if (array[i].equals("Map") || array[i].equals("List") //$NON-NLS-1$ //$NON-NLS-2$
						|| array[i].equals("Set") //$NON-NLS-1$
						|| array[i].equals("Collection")) { //$NON-NLS-1$
					ret = ret + "java.util." + array[i] + ",%20"; //$NON-NLS-1$ //$NON-NLS-2$
				} else {
					ret = ret + array[i] + ",%20"; //$NON-NLS-1$
				}
			} else if (match instanceof Javadoc) {
				ret = ret + ((Javadoc) match).fqn + ",%20"; //$NON-NLS-1$
			} else {
				Javadoc[] docs = (Javadoc[]) match;
				boolean found = false;
				for (int j = 0; j < docs.length; j++) {
					if (array[i].equals(docs[j].fqn)) {
						ret = ret + array[i] + ",%20"; //$NON-NLS-1$
						found = true;
						break;
					}
				}
				if (!found) {
					return null;
				}
			}
		}
		if (ret.endsWith(",%20")) { //$NON-NLS-1$
			ret = ret.substring(0, ret.length() - 4);
		}
		return ret + ')';
	}

	String getDefault() {
		return fqn + " - " + link; //$NON-NLS-1$
	}
	
	public String toString() {
		return fqn;
	}

}