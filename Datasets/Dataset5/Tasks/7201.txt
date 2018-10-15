return "/resources/workflow/incrementalfacade.mwe";

package org.eclipse.xpand.incremental;

public class IncrementalFacadeTest extends AbstractIncrementalTest {
	@Override
	public String getWorkflowFileName() {
		return "/workflow/incrementalfacade.mwe";
	}
	
	@Override
	public boolean writesDiff() {
		return false;
	}
}