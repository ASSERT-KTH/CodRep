package org.jhotdraw.util;

/*
 * @(#)CommandListener.java
 *
 * Project:		JHotdraw - a GUI framework for technical drawings
 *				http://www.jhotdraw.org
 *				http://jhotdraw.sourceforge.net
 * Copyright:	© by the original author(s) and all contributors
 * License:		Lesser GNU Public License (LGPL)
 *				http://www.opensource.org/licenses/lgpl-license.html
 */

package CH.ifa.draw.util;

import java.util.EventObject;

/**
 * @author Wolfram Kaiser
 * @version <$CURRENT_VERSION$>
 */
public interface CommandListener {
	public void commandExecuted(EventObject commandEvent);
	public void commandExecutable(EventObject commandEvent);
	public void commandNotExecutable(EventObject commandEvent);
}