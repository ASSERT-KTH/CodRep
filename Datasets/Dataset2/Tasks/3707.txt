plugin.shutdown();

package org.columba.core.shutdown;

import java.util.Vector;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class ShutdownManager {

	Vector list;
	
	public ShutdownManager()
	{
		list = new Vector();	
	}
	
	public void register( ShutdownPluginInterface plugin )
	{
		list.add( plugin );
	}
	
	public void shutdown()
	{
		for ( int i=0; i<list.size(); i++ )
		{
			ShutdownPluginInterface plugin = (ShutdownPluginInterface) list.get(i);
			
			plugin.run();
		}
		
		System.exit(1);
	}
}