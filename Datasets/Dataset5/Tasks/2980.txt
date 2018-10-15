package org.eclipse.wst.xml.vex.core.internal.util;

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
package org.eclipse.wst.xml.vex.ui.internal.editor;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

/**
 * Data structure that uses two maps to efficiently implement a many-to-many
 * relationship.
 */
public class Association {

	/**
	 * Adds a relationship between two objects.
	 * 
	 * @param left
	 *            Object on the left side of the relationship.
	 * @param right
	 *            Object on the right side of the relationship.
	 */
	public void add(Object left, Object right) {
		Collection rights = (Collection) l2r.get(left);
		if (rights == null) {
			rights = new ArrayList();
			l2r.put(left, rights);
		}
		rights.add(right);

		Collection lefts = (Collection) r2l.get(right);
		if (lefts == null) {
			lefts = new ArrayList();
			r2l.put(right, lefts);
		}
		lefts.add(left);
	}

	/**
	 * Returns a collection of objects on the left side of the association for a
	 * given object on the right.
	 * 
	 * @param right
	 *            Object for which to return associated objects.
	 */
	public Collection getLeftsForRight(Object right) {
		Collection lefts = (Collection) r2l.get(right);
		if (lefts == null) {
			return Collections.EMPTY_LIST;
		} else {
			return Collections.unmodifiableCollection(lefts);
		}
	}

	/**
	 * Returns a collection of objects on the right side of the association for
	 * a given object on the left.
	 * 
	 * @param left
	 *            Object for which to return associated objects.
	 */
	public Collection getRightsForLeft(Object left) {
		Collection rights = (Collection) l2r.get(left);
		if (rights == null) {
			return Collections.EMPTY_LIST;
		} else {
			return Collections.unmodifiableCollection(rights);
		}
	}

	/**
	 * Removes an association between two objects. Returns silently if this is
	 * not an existing relationship.
	 * 
	 * @param left
	 *            Object on the left side of the relationship.
	 * @param right
	 *            Object on the right side of the relationship.
	 */
	public void remove(Object left, Object right) {

		Collection rights = (Collection) l2r.get(left);
		if (rights != null) {
			rights.remove(right);
			if (rights.size() == 0) {
				l2r.remove(left);
			}
		}

		Collection lefts = (Collection) r2l.get(right);
		if (lefts != null) {
			lefts.remove(left);
			if (lefts.size() == 0) {
				r2l.remove(right);
			}
		}

	}

	/**
	 * Removes all relationships for a given object on the left side.
	 * 
	 * @param left
	 *            Object for which to remove a relationship.
	 */
	public void removeLeft(Object left) {

		Collection rights = (Collection) l2r.get(left);
		if (rights == null) {
			return;
		}

		l2r.remove(left);

		for (Iterator it = rights.iterator(); it.hasNext();) {
			Object right = it.next();
			Collection lefts = (Collection) r2l.get(right);
			lefts.remove(left);
			if (lefts.isEmpty()) {
				r2l.remove(right);
			}
		}
	}

	/**
	 * Removes all relationships for a given object on the right side.
	 * 
	 * @param right
	 *            Object for which to remove a relationship.
	 */
	public void removeRight(Object right) {

		Collection lefts = (Collection) r2l.get(right);
		if (lefts == null) {
			return;
		}

		r2l.remove(right);

		for (Iterator it = lefts.iterator(); it.hasNext();) {
			Object left = it.next();
			Collection rights = (Collection) l2r.get(left);
			rights.remove(right);
			if (rights.isEmpty()) {
				l2r.remove(left);
			}
		}
	}

	// ==================================================== PRIVATE

	// maps left => list of associated rights
	private Map l2r = new HashMap();

	// maps right => list of associated lefts
	private Map r2l = new HashMap();
}