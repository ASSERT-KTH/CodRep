((MailFrameController) frameMediator).registerTreeSelectionListener(

/*
 * Created on 11.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.tree.action;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.gui.tree.selection.TreeSelectionChangedEvent;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class SubscribeFolderAction
	extends FrameAction
	implements SelectionListener {

	public SubscribeFolderAction(AbstractFrameController frameController) {
		super(
				frameController,
				MailResourceLoader.getString(
					"menu", "mainframe", "menu_folder_subscribe"));

		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "mainframe", "menu_folder_subscribe"));
		
		// action command
		setActionCommand("SUBSCRIBE");
		
		// icons
		setSmallIcon(ImageLoader.getSmallImageIcon("remotehost.png"));
		setLargeIcon(ImageLoader.getImageIcon("remotehost.png"));

		// shortcut key
		setAcceleratorKey(
				KeyStroke.getKeyStroke(KeyEvent.VK_S, ActionEvent.ALT_MASK));
		
		setEnabled(false);
		// FIXME
		//  -> uncomment to enable/disable action
		/*
		((MailFrameController) frameController).registerTreeSelectionListener(
			this);
		*/
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {

	}
	/* (non-Javadoc)
					 * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
					 */
	public void selectionChanged(SelectionChangedEvent e) {

		if (((TreeSelectionChangedEvent) e).getSelected().length > 0)
			setEnabled(true);
		else
			setEnabled(false);

	}
}