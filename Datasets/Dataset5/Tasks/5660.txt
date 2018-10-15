final class GlobalVarContextImpl implements GlobalVarContext {

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.xtend.backend.common.GlobalVarContext;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class GlobalVarContextImpl implements GlobalVarContext {
	private final Map<String, Object> _globalVars = new HashMap<String, Object> ();

	public Map<String, Object> getGlobalVars() {
		return _globalVars;
	}
}