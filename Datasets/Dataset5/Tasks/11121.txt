package org.eclipse.xtend.profiler;

/*******************************************************************************
 * Copyright (c) 2009 itemis AG (http://www.itemis.eu) and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 *******************************************************************************/

package org.eclipse.xtend.util.stdlib.profiler;

import junit.framework.TestCase;

import org.eclipse.xtend.profiler.CycleDetector;
import org.eclipse.xtend.profiler.profilermodel.CallGroup;
import org.eclipse.xtend.profiler.profilermodel.Cycle;
import org.eclipse.xtend.profiler.profilermodel.Item;
import org.eclipse.xtend.profiler.profilermodel.ModelFactory;
import org.eclipse.xtend.profiler.profilermodel.ProfilingResult;

/**
 * @author Heiko Behrens - Initial contribution and API
 */
public class CycleDetectorTest extends TestCase { 
	ProfilingResult pResult = ModelFactory.eINSTANCE.createProfilingResult();
	CycleDetector detector = new CycleDetector(pResult);
	
	public void testEmpty() throws Exception {
		detector.detectCycles();
		assertEquals(0, pResult.getCycles().size());
	}

	public void testTrivial() throws Exception {
		createItem("a");
		detector.detectCycles();
		assertEquals(0, pResult.getCycles().size());
	}

	public void testPath() throws Exception {
		createEdge("a", "b").expandTo("c");
		assertEquals(3, pResult.getItems().size());
		detector.detectCycles();
		assertEquals(0, pResult.getCycles().size());
	}
	
	public void testMiniCycle() throws Exception {
		Item a = createItem("a");
		Item b = createItem("b");
		createEdge(a, b);
		createEdge(b, a);
		detector.detectCycles();
		assertEquals(1, pResult.getCycles().size());
		
		Cycle c = pResult.getCycles().get(0);
		assertEquals(2, c.getItems().size());
		assertTrue(c.getItems().contains(a));
		assertTrue(c.getItems().contains(b));
		assertEquals("a;b;", getCycleAsString(c));
	}
	
	public void testSelfRecursion() throws Exception {
		Item b = createItem("b");
		createEdge(createItem("a"), b).expandTo("c");
		createEdge(b, b);
		assertEquals(3, pResult.getItems().size());
		
		detector.detectCycles();
		assertEquals(1, pResult.getCycles().size());
		
		Cycle c = pResult.getCycles().get(0);
		assertEquals(1, c.getItems().size());
		assertTrue(c.getItems().contains(b));
	}
	
	public void testGProfCycleExample() throws Exception {
		// example from http://www.cs.utah.edu/dept/old/texinfo/as/gprof.html#SEC10
		Item a = createItem("a");
		Item b = createItem("b");
		Item c = createItem("c");
		createEdge("start", "main").expandTo(a).expandTo(b).expandTo(c);
		createEdge(b, a).expandTo(c);
		
		assertEquals(5, pResult.getItems().size());
		detector.detectCycles();
		assertEquals(1, pResult.getCycles().size());
		assertEquals("a;b;", getCycleAsString(pResult.getCycles().get(0)));
	}
	
	public void testCallingCycles() throws Exception {
		Item connection = createItem("conection");
		Item a = createItem("a");
		Item b = createItem("b");
		Item u = createItem("u");
		Item v = createItem("v");
		
		createEdge(a, b).expandTo(a);
		createEdge(u, v).expandTo(u);
		createEdge(b, connection).expandTo(u);
		
		detector.detectCycles();
		assertEquals(2, pResult.getCycles().size());
		assertEquals("a;b;", getCycleAsString(pResult.getCycles().get(0)));
		assertEquals("u;v;", getCycleAsString(pResult.getCycles().get(1)));
	}
	
	protected void dumpCycles() {
		System.out.println(pResult.getCycles().size() + " cycle(s)");
		for (Cycle c : pResult.getCycles()) {
			System.out.println(getCycleAsString(c));
		}
	}

	private String getCycleAsString(Cycle c) {
		String result = "";
		for (Item i : c.getItems()) {
			result += i.getItemName() + ";";
		}
		return result ;
	}

	class Edge {
		final Item from;
		final Item to;
		
		Edge(Item from, Item to) {
			this.from = from;
			this.to = to;
			CallGroup group = ModelFactory.eINSTANCE.createCallGroup();
			group.setSubroutine(to);
			from.getSubroutines().add(group);
		}
		
		Edge expandTo(Item to) {
			return new Edge(this.to, to);
		}
		
		Edge expandTo(String to) {
			return expandTo(createItem(to));
		}
		
	}
	
	private Edge createEdge(String from, String to) {
		return createEdge(createItem(from), createItem(to));
	}

	private Edge createEdge(Item from, Item to) {
		return new Edge(from, to);
	}

	private Item createItem(String name) {
		Item result = ModelFactory.eINSTANCE.createItem();
		result.setItemName(name);
		pResult.getItems().add(result);
		return result;
	}
}