import org.eclipse.xtend.middleend.javaannotations.AbstractExecutionContextAware;

package org.eclipse.xtend.middleend.xtend.internal.xtendlib;

import java.util.Map;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.eclipse.xtend.backend.functions.java.AbstractExecutionContextAware;


public class XtendGlobalVarOperations extends AbstractExecutionContextAware {
    public static final Class<?> GLOBAL_VAR_VALUES_KEY = new Object(){}.getClass ();
    final Log _log = LogFactory.getLog(getClass());
    
    public Object XtendGlobalVar (String varName) {
        @SuppressWarnings("unchecked")
        final Map<String, Object> globalParams = (Map<String, Object>) _ctx.getContributionStateContext().retrieveState (GLOBAL_VAR_VALUES_KEY);
        if (globalParams == null)
            return null;
        
        final Object result = globalParams.get (varName);
        
        if (_log.isDebugEnabled())
            _log.debug ("retrieving global var " + varName + ": " + result);
        
        return result;
    }
}