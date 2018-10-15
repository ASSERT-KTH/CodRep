Item sub = group.getSubroutine();

/*******************************************************************************
 * Copyright (c) 2009 itemis AG (http://www.itemis.eu) and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 *******************************************************************************/
package org.eclipse.xtend.profiler;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.eclipse.xtend.profiler.profilermodel.CallGroup;
import org.eclipse.xtend.profiler.profilermodel.Cycle;
import org.eclipse.xtend.profiler.profilermodel.Item;
import org.eclipse.xtend.profiler.profilermodel.ModelFactory;
import org.eclipse.xtend.profiler.profilermodel.ProfilingResult;


/**
 * Detects cycles in call graph of a given profiling result. This implementation uses
 * a slightly modified Tarjan's strongly connected components (SCC) algorithm to accept
 * trivial SCCs only if there is an reflexive edge (self recursion).
 * 
 * @see http://en.wikipedia.org/wiki/Tarjan's_strongly_connected_components_algorithm
 * @author Heiko Behrens - Initial contribution and API
 */
public class CycleDetector {
	private final ProfilingResult profilingResult;

	public CycleDetector(ProfilingResult result) {
		profilingResult = result;
	}
		
	private void tarjan(Item item) {
		visited.add(item);
		setLowLink(item, getIndex(item));
		stack.add(0, item);
		for (CallGroup group : item.getSubroutines()) {
			Item sub = (Item)group.getSubroutine();
			if (!hasBeenVisited(sub)) {
				tarjan(sub);
				setLowLinkIfSmaller(item, getLowLink(sub));
			} else if(stack.contains(sub))
				setLowLinkIfSmaller(item, getIndex(sub));
		}
		
		if(getLowLink(item) == getIndex(item))
			buildCycleFromStack(item);
	}

	private void buildCycleFromStack(Item item) {
		List<Item> items = new ArrayList<Item>();
		while (true) {
			Item v = stack.remove(0);
			// use inverted order to support human's understanding
			items.add(0, v);
			if (item.equals(v))
				break;
		}
		if (items.size() > 1 || isSelfRecursion(item)) {
			Cycle cycle = ModelFactory.eINSTANCE.createCycle();
			cycle.getItems().addAll(items);
			// use inverted order to support human's understanding
			profilingResult.getCycles().add(0, cycle);
		}
	}
	
	private boolean isSelfRecursion(Item item) {
		for (CallGroup g : item.getSubroutines())
			if (item.equals(g.getSubroutine()))
				return true;
		return false;
	}

	List<Item> visited = new ArrayList<Item>();
	List<Item> stack = new ArrayList<Item>();
	Map<Item, Integer> lowLink = new HashMap<Item, Integer>(); 
	
	public void detectCycles() {
		profilingResult.getCycles().clear();
		Set<Item> toBeVisited = new LinkedHashSet<Item>(profilingResult.getItems());
		while(!toBeVisited.isEmpty()) {
			Item item = toBeVisited.iterator().next();
			tarjan(item);	
			toBeVisited.removeAll(visited);
		}
	}
	
	private void setLowLink(Item item, int value) {
		lowLink.put(item, value);
	}
	
	private void setLowLinkIfSmaller(Item item, int potentiallySmallerValue) {
		setLowLink(item, Math.min(getLowLink(item), potentiallySmallerValue));
	}
	
	private int getLowLink(Item item) {
		return lowLink.get(item);
	}

	private boolean hasBeenVisited(Item item) {
		return visited.contains(item);
	}
	
	private int getIndex(Item item) {
		if(!hasBeenVisited(item))
			throw new IllegalStateException("Item has not been visited, yet.");
		return visited.indexOf(item);
	}

}