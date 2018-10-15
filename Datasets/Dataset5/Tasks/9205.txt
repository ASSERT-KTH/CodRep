sb.append("]");//$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2008 Marcelo Mayworm. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: 	Marcelo Mayworm - initial API and implementation
 *
 ******************************************************************************/
package org.eclipse.ecf.internal.provider.xmpp.search;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;

import org.eclipse.ecf.presence.search.ICriteria;
import org.eclipse.ecf.presence.search.ICriterion;

/**
 * Implement a specific criteria control for XMPP
 *@since 3.0
 */
public class XMPPCriteria implements ICriteria {

	/** criteria list */
	protected List criteria;
	
	/**
	 * Create a criteria with a sync list
	 */
	public XMPPCriteria(){
		criteria = Collections.synchronizedList(new ArrayList());
	}
	
	/*
	 * (non-Javadoc)
	 * @see org.eclipse.ecf.presence.search.ICriteria#add(org.eclipse.ecf.presence.search.ICriterion)
	 */
	public void add(ICriterion criterion) {
		criteria.add(criterion);
	}

	/*
	 * (non-Javadoc)
	 * @see org.eclipse.ecf.presence.search.ICriteria#getCriterions()
	 */
	public List getCriterions() {
		return criteria;
	}

	/*
	 * (non-Javadoc)
	 * @see org.eclipse.ecf.presence.search.ICriteria#isEmpty()
	 */
	public boolean isEmpty() {
		return criteria.isEmpty();
	}
	
	public String toString() {
		StringBuffer sb = new StringBuffer("XMPPCriteria["); //$NON-NLS-1$
		Iterator it = criteria.iterator();
		while (it.hasNext()) {
			sb.append("[");//$NON-NLS-1$
			ICriterion criterion = (ICriterion) it.next();
			sb.append(criterion.toString());
			sb.append("];");//$NON-NLS-1$
		}
		sb.append("];");//$NON-NLS-1$
		return sb.toString();
	}

}