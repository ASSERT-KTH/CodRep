public abstract class AbstractFrameController implements FrameMediator{

//The contents of this file are subject to the Mozilla Public License Version 1.1
//(the "License"); you may not use this file except in compliance with the 
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003. 
//
//All Rights Reserved.

package org.columba.core.gui.frame;

import java.awt.event.MouseAdapter;

import org.columba.core.config.ViewItem;
import org.columba.core.gui.menu.Menu;
import org.columba.core.gui.selection.SelectionManager;
import org.columba.core.gui.statusbar.StatusBar;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.core.xml.XmlElement;
import org.columba.mail.gui.frame.TooltipMouseHandler;

/**
 * The Controller is responsible for creating a view.
 * 
 * It provides a selection handler facility through a 
 * {@link SelectionManager}.
 * 
 * @see org.columba.core.gui.selection.SelectionManager
 * 
 * @author Timo Stich (tstich@users.sourceforge.net)
 * 
 */
public abstract class AbstractFrameController {

	protected StatusBar statusBar;
	
	/**
	 * Menuitems use this to display a string in the statusbar
	 */
	protected MouseAdapter mouseTooltipHandler;

	/**
	 * Saves view information like position, size and maximization state
	 */
	protected ViewItem viewItem;

	/**
	 * 
	 * View this controller handles
	 */
	protected AbstractFrameView view;
	
	/**
	 * Selection handler
	 */
	protected SelectionManager selectionManager;
	
	/**
	 * ID of controller
	 */
	protected String id;

	/**
	 * Constructor for FrameController.
	 * 
	 * Warning: Never do any inits in the constructor -> use init() instead!
	 * 
	 * The problem is that we have some circular dependencies here:
	 * The view needs the action to be initializied first.
	 * The actions need the controller properly initialized.
	 * 
	 * So, take care when changing the order of initialization
	 * 
	 */
	public AbstractFrameController(String id, ViewItem viewItem) {
		this.id = id;
		this.viewItem = viewItem;

		// If no view spec. is given, use default
		if (viewItem == null)
			this.viewItem = new ViewItem(createDefaultConfiguration(id));

		// register statusbar at global taskmanager
		statusBar = new StatusBar(MainInterface.processor.getTaskManager());

		// add tooltip handler
		mouseTooltipHandler = new TooltipMouseHandler(statusBar);

		// init selection handler
		selectionManager = new SelectionManager();
		
		// initialize the view here
		init();

		// initialize all actions
		initActions();
		
		// create view
		view = createView();
		
	}

	/**
	 * 
	 * @see ThreePaneMailFrameController for an example of its usage
	 *
	 */
	protected void initActions() {
	}

	/**
	 * 
	 * Create default view configuration
	 * 
	 * This is used by implementations of controllers who want
	 * to store some more information, which is specific to their
	 * domain.
	 * 
	 * @see AbstractMailFrameController for implementation example
	 * 
	 * 
	 * @param id	ID of controller
	 * @return		xml treenode containing the new configuration
	 */
	protected XmlElement createDefaultConfiguration(String id) {
		/* *20030831, karlpeder* Moved code here from constructor
		XmlElement child = (XmlElement) defaultView.clone();
		child.addAttribute("id", id);
		*/
		
		// initialize default view options
		XmlElement defaultView = new XmlElement("view");
		XmlElement window = new XmlElement("window");
		window.addAttribute("width", "640");
		window.addAttribute("height", "480");
		window.addAttribute("maximized", "true");
		defaultView.addElement(window);
		XmlElement toolbars = new XmlElement("toolbars");
		toolbars.addAttribute("main","true");
		defaultView.addElement(toolbars);

		defaultView.addAttribute("id", id);

		return defaultView;
	}


	/**
	 * - create all additional controllers
	 * - register SelectionHandlers
	 */
	protected abstract void init();


	/**
	 * 
	 * @return	statusbar
	 */
	public StatusBar getStatusBar() {
		return statusBar;
	}

	/**
	 * Returns the mouseTooltipHandler.
	 * 
	 * @return MouseAdapter
	 */
	public MouseAdapter getMouseTooltipHandler() {
		return mouseTooltipHandler;
	}

	/* *20030831, karlpeder* Not used, close method is used instead
	public void saveAndClose() {
		view.saveWindowPosition();
	}
	*/

	/**
	 * Save window properties and close the window.
	 * This includes telling the frame model that
	 * this window/frame is closing, so it can be
	 * "unregistered" correctly
	 */
	public void close() {
        ColumbaLogger.log.info("Closing FrameController: " + 
        		this.getClass().getName());
		view.saveWindowPosition(); // ask view to store current pos and size
		view.setVisible(false);
		/*
		 * Tell frame model that frame is closing.
		 * If this frame hasn't been opened using FrameModel methods,
		 * FrameModel.close does nothing.
		 */		
		FrameModel.close(this); 
	}

	/**
	 * Create view 
	 * 
	 * @return	view object
	 */
	abstract protected AbstractFrameView createView();

	/**
	 * Open new view.
	 *
	 */
	public void openView() {
		view.loadWindowPosition();
		

		view.setVisible(true);
		
		// set the position afterwards
		// if not the maximization fails
		view.loadWindowPosition();
	}

	/**
	 * @return ViewItem
	 */
	public ViewItem getViewItem() {
		return viewItem;
	}

	/**
	 * Sets the item.
	 * @param item The item to set
	 */
	public void setViewItem(ViewItem item) {
		this.viewItem = item;
	}
	
	/**
	 * Enable/Disable toolbar configuration
	 * 
	 * @param id		ID of controller
	 * @param enable	true/false
	 */
	public void enableToolbar(String id, boolean enable)
	{
		getViewItem().set("toolbars", id, enable);
	}
	
	/**
	 * Returns true if the toolbar is enabled
	 * 
	 * @param id		ID of controller
	 * @return			true, if toolbar is enabled, false otherwise
	 */
	public boolean isToolbarEnabled(String id)
	{
		return getViewItem().getBoolean("toolbars", id, true);
	}

	/**
	 * @return FrameView
	 */
	public AbstractFrameView getView() {
		return view;
	}

	public Menu getMenu() {
		return view.getMenu();
	}

	/**
	 * @return SelectionManager
	 */
	public SelectionManager getSelectionManager() {
		return selectionManager;
	}

	/**
	 * Sets the selectionManager.
	 * @param selectionManager The selectionManager to set
	 */
	public void setSelectionManager(SelectionManager selectionManager) {
		this.selectionManager = selectionManager;
	}
}