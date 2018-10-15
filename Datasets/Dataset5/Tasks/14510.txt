if (!(o instanceof Pair<?, ?>))

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
 * This class provides combines two objects into one, giving them appropriate
 * equals and hashCode methods.
 * 
 * @author Arno Haase
 */
public class Pair<T1, T2> implements Serializable, Cloneable {
	private static final long serialVersionUID = 5892226218172864652L;

	private T1 _first;

	private T2 _second;

	public Pair() {
	}

	public Pair(T1 first, T2 second) {
		_first = first;
		_second = second;
	}

	public T1 getFirst() {
		return _first;
	}

	public void setFirst(T1 first) {
		_first = first;
	}

	public T2 getSecond() {
		return _second;
	}

	public void setSecond(T2 second) {
		_second = second;
	}

	public String toString() {
		return "Pair [" + _first + ", " + _second + "]";
	}

	public boolean equals(Object o) {
		if (this == o)
			return true;
		if (!(o instanceof Pair))
			return false;

		final Pair<?, ?> pair = (Pair<?, ?>) o;

		if (_first != null ? !_first.equals(pair._first) : pair._first != null)
			return false;
		if (_second != null ? !_second.equals(pair._second) : pair._second != null)
			return false;

		return true;
	}

	public int hashCode() {
		int result;
		result = (_first != null ? _first.hashCode() : 0);
		result = 29 * result + (_second != null ? _second.hashCode() : 0);
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