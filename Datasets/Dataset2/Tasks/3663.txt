public void shutdown() {

package org.columba.core.shutdown;

import org.columba.core.config.Config;
import org.columba.core.shutdown.*;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class SaveConfigPlugin implements ShutdownPluginInterface {

	/**
	 * @see org.columba.core.gui.ShutdownPluginInterface#run()
	 */
	public void run() {
		try {

			Config.save();
		} catch (Exception ex) {
			ex.printStackTrace();

		}
	}

}