setAttribute(FigureAttributeConstant.FRAME_COLOR.getName(), Color.red);

/*
 * @(#)PertDependency.java
 *
 * Project:		JHotdraw - a GUI framework for technical drawings
 *				http://www.jhotdraw.org
 *				http://jhotdraw.sourceforge.net
 * Copyright:	© by the original author(s) and all contributors
 * License:		Lesser GNU Public License (LGPL)
 *				http://www.opensource.org/licenses/lgpl-license.html
 */

package CH.ifa.draw.samples.pert;

import java.awt.*;
import java.util.*;
import java.io.IOException;
import CH.ifa.draw.framework.*;
import CH.ifa.draw.figures.*;
import CH.ifa.draw.standard.*;

/**
 * @version <$CURRENT_VERSION$>
 */
public class PertDependency extends LineConnection {
	/*
	 * Serialization support.
	 */
	private static final long serialVersionUID = -7959500008698525009L;
	private int pertDependencySerializedDataVersion = 1;

	public PertDependency() {
		setEndDecoration(new ArrowTip());
		setStartDecoration(null);
	}

	public void handleConnect(Figure start, Figure end) {
		PertFigure source = (PertFigure)start;
		PertFigure target = (PertFigure)end;
		if (source.hasCycle(target)) {
			setAttribute("FrameColor", Color.red);
		}
		else {
			target.addPreTask(source);
			source.addPostTask(target);
			source.notifyPostTasks();
		}
	}

	public void handleDisconnect(Figure start, Figure end) {
		PertFigure source = (PertFigure)start;
		PertFigure target = (PertFigure)end;
		if (target != null) {
			target.removePreTask(source);
			target.updateDurations();
		}
		if (source != null) {
			source.removePostTask(target);
		}
   }

	public boolean canConnect(Figure start, Figure end) {
		return ((start instanceof PertFigure) && (end instanceof PertFigure));
	}

	public Vector handles() {
		Vector handles = super.handles();
		// don't allow to reconnect the starting figure
		handles.setElementAt(new NullHandle(this, PolyLineFigure.locator(0)), 0);
		return handles;
	}
}