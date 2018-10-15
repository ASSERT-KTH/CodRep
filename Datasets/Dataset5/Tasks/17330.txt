public static final String VARIABLE = "sdk_version";

package org.eclipse.wst.xquery.set.internal.launching.variables;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.variables.IDynamicVariable;
import org.eclipse.core.variables.IDynamicVariableResolver;

public class CoreSdkVersionResolver implements IDynamicVariableResolver {

    public static final String VARIABLE = "${sdk_version}";
    public static final String VERSION = "1.0.14";

    public String resolveValue(IDynamicVariable variable, String argument) throws CoreException {
        return VERSION;
    }

}