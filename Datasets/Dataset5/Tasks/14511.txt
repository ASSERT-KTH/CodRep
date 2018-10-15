if (!(o instanceof Triplet<?, ?, ?>))

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/
package org.eclipse.internal.xtend.util;

import java.io.Serializable;

/**
 * This class provides combines three objects into one, giving them appropriate
 * equals and hashCode methods.
 * 
 * @author Arno Haase
 */
public class Triplet<T1, T2, T3> implements Serializable, Cloneable {
	private static final long serialVersionUID = -3721045730655830208L;

	private T1 _first;

	private T2 _second;

	private T3 _third;

	public Triplet(T1 first, T2 second, T3 third) {
		_first = first;
		_second = second;
		_third = third;
	}

	public T1 getFirst() {
		return _first;
	}

	public T2 getSecond() {
		return _second;
	}

	public T3 getThird() {
		return _third;
	}

	public void setFirst(T1 first) {
		_first = first;
	}

	public void setSecond(T2 second) {
		_second = second;
	}

	public void setThird(T3 third) {
		_third = third;
	}

	public String toString() {
		return "Triplet [" + _first + ", " + _second + ", " + _third + "]";
	}

	public boolean equals(Object o) {
		if (this == o)
			return true;
		if (!(o instanceof Triplet))
			return false;

		final Triplet<?, ?, ?> triplet = (Triplet<?, ?, ?>) o;

		if (_first != null ? !_first.equals(triplet._first) : triplet._first != null)
			return false;
		if (_second != null ? !_second.equals(triplet._second) : triplet._second != null)
			return false;
		if (_third != null ? !_third.equals(triplet._third) : triplet._third != null)
			return false;

		return true;
	}

	public int hashCode() {
		int result;
		result = (_first != null ? _first.hashCode() : 0);
		result = 29 * result + (_second != null ? _second.hashCode() : 0);
		result = 29 * result + (_third != null ? _third.hashCode() : 0);
		return result;
	}

	public Object clone() {
		try {
			return super.clone();
		} catch (CloneNotSupportedException e) {
			throw new InternalError("Should not be thrown: " + e);
		}
	}
}