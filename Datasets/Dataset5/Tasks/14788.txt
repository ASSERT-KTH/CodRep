final IConfigurationElement[] confEl = RegistryFactory.getRegistry().getConfigurationElementsFor ("org.eclipse.xtend.backend.MiddleEnd");

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipose.xtend.middleend.internal;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.eclipose.xtend.middleend.plugins.LanguageSpecificMiddleEnd;
import org.eclipose.xtend.middleend.plugins.LanguageSpecificMiddleEndFactory;
import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.core.runtime.RegistryFactory;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public class Activator implements BundleActivator {
    private static final Log _log = LogFactory.getLog (Activator.class);
    
    private static Activator _instance = null;
    
    public static Activator getInstance () {
        return _instance;
    }

    private final List<LanguageSpecificMiddleEndFactory> _middleEndContributions = new ArrayList<LanguageSpecificMiddleEndFactory> ();
    private boolean _isInitialized = false;

    
    public List<LanguageSpecificMiddleEnd> getFreshMiddleEnds (Map<Class<?>, Object> specificParams) {
        init ();
        
        final List<LanguageSpecificMiddleEnd> result = new ArrayList<LanguageSpecificMiddleEnd>();
        
        for (LanguageSpecificMiddleEndFactory factory: _middleEndContributions) {
            try {
                result.add (factory.create (specificParams.get (factory.getClass())));
            }
            catch (IllegalArgumentException exc) {
                // this is the official way for an implementation to withdraw from the pool for this call
                _log.debug ("middle end implementation " + factory.getName() + " says it is not available: " + exc.getMessage());
            }
        }
        
        return result;
    }
    
    public void start (BundleContext context) throws Exception {
        //TODO Bernd: implement error handling and logging to be both robust and independent of Eclipse
        
        _isInitialized = false;
        _instance = this;
    }
    
    private void init () {
        if (_isInitialized)
            return;
        
        _isInitialized = true;
        _middleEndContributions.clear ();

        try {
            final IConfigurationElement[] confEl = RegistryFactory.getRegistry().getConfigurationElementsFor ("org.eclipse.xtend.middleend.MiddleEnd");

            for (IConfigurationElement curEl: confEl) {
                final Object o = curEl.createExecutableExtension ("class");
                _middleEndContributions.add ((LanguageSpecificMiddleEndFactory) o);
            }
        }
        catch (Exception exc) {
            exc.printStackTrace ();
        }
        
        Collections.sort (_middleEndContributions, new Comparator <LanguageSpecificMiddleEndFactory> () {
            public int compare (LanguageSpecificMiddleEndFactory o1, LanguageSpecificMiddleEndFactory o2) {
                return o1.getPriority() - o2.getPriority();
            }
        });
        
        _log.info ("Activating Eclipse Modeling Middle End - the following middle ends are registered:");
        for (LanguageSpecificMiddleEndFactory factory: _middleEndContributions)
            _log.info ("  " + factory.getName());
    }

    public void stop (BundleContext context) throws Exception {
        _instance = null;
        _middleEndContributions.clear();
    }
}