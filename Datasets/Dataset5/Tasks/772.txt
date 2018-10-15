.addRegisterEcoreFile("platform:/resource/eclipse.xtend.util.stdlib/src/org/eclipse/xtend/util/stdlib/trace.ecore");

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
package org.eclipse.xtend.util.stdlib;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.Stack;

import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.mwe.core.WorkflowContext;
import org.eclipse.emf.mwe.core.issues.Issues;
import org.eclipse.emf.mwe.core.monitor.ProgressMonitor;
import org.eclipse.emf.mwe.utils.AbstractEMFWorkflowComponent;
import org.eclipse.emf.mwe.utils.StandaloneSetup;
import org.eclipse.xtend.util.stdlib.tracing.M2CTraceElement;
import org.eclipse.xtend.util.stdlib.tracing.M2MTraceElement;
import org.eclipse.xtend.util.stdlib.tracing.MapList;
import org.eclipse.xtend.util.stdlib.tracing.TraceElement;
import org.eclipse.xtend.util.stdlib.tracing.TraceStore;

public class TraceComponent extends AbstractEMFWorkflowComponent {

	private static final String COMPONENT_NAME = "Trace Component";

	private String traceModelSlotName;
	private String traceName;
	private static TraceStore traceStore = new TraceStore();
	private static Stack<String> fileStack = new Stack<String>();
	private static int tokenValue = 0;
	private static MapList cache = new MapList();

	public static void createTrace(Object from, Object to, String kind) {
		TraceElement t = new M2MTraceElement(kind, (EObject) from, (EObject) to);
		traceStore.add(t);
	}

	public static void createTrace(Object from, Collection to, String kind) {
		TraceElement t = new M2MTraceElement(kind, (EObject) from, (Collection<EObject>) to);
		traceStore.add(t);
	}

	public static void createTrace(Collection from, Object to, String kind) {
		TraceElement t = new M2MTraceElement(kind, (Collection<EObject>) from, (EObject) to);
		traceStore.add(t);
	}

	public static String createCodeTrace(Object from, String kind) {
		if (!fileStack.isEmpty()) {
			String currentFile = fileStack.peek();
			String token = createNewToken();
			TraceElement t = new M2CTraceElement(kind, (EObject) from, currentFile, token);
			traceStore.add(t);
			return token;
		}
		return "<unknown>";
	}

	private static String createNewToken() {
		return "TRACE_" + (tokenValue++);
	}

	public static Object getSingleTraceTarget(Object from, String kind) {
		List traces = traceStore.getTraces(from, kind);
		if (traces.size() == 0)
			return null;
		M2MTraceElement e = (M2MTraceElement) traces.get(0);
		return e.getTargets().get(0);
	}

	public static Object getTraceTargets(Object from, String kind) {
		List traces = traceStore.getTraces(from, kind);
		List targets = new ArrayList();
		for (Iterator iterator = traces.iterator(); iterator.hasNext();) {
			M2MTraceElement te = (M2MTraceElement) iterator.next();
			targets.addAll(te.getTargets());
		}
		return targets;
	}

	@Override
	public String getLogMessage() {
		return "building trace model in slot '" + traceModelSlotName + "'";
	}

	public static void clearTrace() {
		traceStore.clear();
	}

	public void setTraceModelSlot(String slot) {
		this.traceModelSlotName = slot;
	}

	public void setTraceName(String name) {
		this.traceName = name;
	}

	@Override
	public void checkConfiguration(Issues issues) {
		if (traceModelSlotName == null) {
			issues.addError(this, "you have to specify a traceModelSlot");
		}
		if (traceName == null) {
			issues.addError(this, "you have to specify a traceName");
		}
	}

	@Override
	public void invokeInternal(WorkflowContext ctx, ProgressMonitor mon, Issues issues) {
		setUseSingleGlobalResourceSet(true);
		try {
			StandaloneSetup setup = new StandaloneSetup();
			setup
					.addRegisterEcoreFile("platform:/resource/eclipse.xtend.util.stdlib/src/org/openarchitectureware/util/stdlib/trace.ecore");
			EPackage pack = setup.getPackage("http://openarchitectureware.org/trace");
			DynamicEcoreHelper h = new DynamicEcoreHelper(pack);
			EObject model = h.create("Trace");
			createElementList(h, model);
			createBySource(h, model);
			ctx.set(traceModelSlotName, model);
		}
		catch (Exception e) {
			issues.addError(this, e.getMessage());
		}
	}

	private void createBySource(DynamicEcoreHelper h, EObject model) {
		for (Iterator iter = cache.getKeys().iterator(); iter.hasNext();) {
			EObject source = (EObject) iter.next();
			EObject bySource = h.create("TraceBySource");
			h.set(bySource, "source", source);
			Collection traces = cache.get(source);
			for (Iterator iterator = traces.iterator(); iterator.hasNext();) {
				EObject item = (EObject) iterator.next();
				h.add(bySource, "items", item);
			}
			h.add(model, "traceBySource", bySource);
		}
	}

	private void createElementList(DynamicEcoreHelper h, EObject model) {
		EObject list = h.create("TraceList");
		h.set(model, "list", list);
		for (Iterator iter = traceStore.getAllTraces().iterator(); iter.hasNext();) {
			TraceElement element = (TraceElement) iter.next();
			EObject item = null;
			if (element instanceof M2MTraceElement) {
				M2MTraceElement m2m = (M2MTraceElement) element;
				item = h.create("M2MTraceItem");
				h.set(item, "kind", m2m.getKind());
				h.addAll(item, "from", m2m.getSources());
				h.addAll(item, "to", m2m.getTargets());
				h.add(list, "items", item);
			}
			else {
				M2CTraceElement m2c = (M2CTraceElement) element;
				item = h.create("M2CTraceItem");
				h.set(item, "kind", m2c.getKind());
				h.addAll(item, "from", m2c.getSources());
				h.set(item, "targetFile", m2c.getFileName());
				h.set(item, "token", m2c.getToken());
				h.add(list, "items", item);
			}
			for (Iterator<EObject> iterator = element.getSources().iterator(); iterator.hasNext();) {
				EObject source = iterator.next();
				cache.add(source, item);
			}
		}
	}

	public static void reportFileOpen(String path) {
		fileStack.push(path);
	}

	public static void reportFileClose() {
		fileStack.pop();
	}

	@Override
	public String getComponentName() {
		return COMPONENT_NAME;
	}
}