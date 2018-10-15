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

import java.io.Serializable;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Represents a state in a deterministic finite automaton (DFA). A DFA can be
 * thought of as a directed graph, where each arc in the graph represents a
 * transition on an input symbol to a new state (i.e. a node in the graph.) The
 * DFA has a start state and one or more accepting states. The DFA represents a
 * grammar. If a sequence of input symbols drives the DFA from the start state
 * to one of the accepting states, the sequence is a valid sentence in the
 * grammar represented by the DFA.
 * 
 * <p>
 * Within VEX, we use a DFA to validate the sequence of children of a given
 * element. A DFA is constructed for each element declaration in the DTD.
 * </p>
 */
public class DFAState implements Serializable {

	private boolean accepting = false;
	private Map transitions = new HashMap();

	/**
	 * Class constructor.
	 */
	public DFAState() {
	}

	/**
	 * Return the state obtained by traversing the given list of symbols.
	 * Returns null if the given sequence does not lead to a state in the DFA.
	 * 
	 * @param sequence
	 *            Sequence of symbols to use.
	 */
	public DFAState getState(List sequence) {
		DFAState state = this;
		Iterator iter = sequence.iterator();
		while (iter.hasNext()) {
			state = state.getNextState(iter.next());
			if (state == null) {
				break;
			}
		}
		return state;
	}

	/**
	 * Adds an outgoing transition to the state.
	 * 
	 * @param symbol
	 *            Symbol that initiates the transition.
	 * @param target
	 *            State to which the transition leads.
	 */
	public void addTransition(Object symbol, DFAState target) {
		this.transitions.put(symbol, target);
	}

	/**
	 * Returns the set of symbols that are valid for this state.
	 */
	public Set getValidSymbols() {
		return this.transitions.keySet();
	}

	/**
	 * Returns true if this is an accepting state of the DFA.
	 */
	public boolean isAccepting() {
		return this.accepting;
	}

	/**
	 * Returns the next state given the given input symbol, or null if there are
	 * no outgoing transitions corresponding to the given symbol.
	 * 
	 * @param symbol
	 *            input symbol
	 */
	public DFAState getNextState(Object symbol) {
		return (DFAState) this.transitions.get(symbol);
	}

	/**
	 * Sets the value of the accepting property.
	 * 
	 * @param accepting
	 *            true if this an accepting state of the DFA.
	 */
	public void setAccepting(boolean accepting) {
		this.accepting = accepting;
	}

	// ========================================================= PRIVATE

}