return new CoreSdkDebuggerRunner(install);

package org.eclipse.wst.xquery.set.debug.debugger;

import org.eclipse.dltk.launching.IInterpreterInstall;
import org.eclipse.dltk.launching.IInterpreterRunner;
import org.eclipse.dltk.launching.IInterpreterRunnerFactory;

public class SETDebuggerRunnerFactory implements IInterpreterRunnerFactory {

    public IInterpreterRunner createRunner(IInterpreterInstall install) {
        return new SETDebuggerRunner(install);
    }

}