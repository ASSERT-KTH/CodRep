import org.columba.ristretto.message.HeaderInterface;

/*
 * SaveMessageBodyAsCommand.java
 * Created 2003-06-20
 */
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

package org.columba.mail.folder.command;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.StatusObservableImpl;
import org.columba.core.command.Worker;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.xml.XmlElement;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.filter.Filter;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.config.filter.FilterDialog;
import org.columba.mail.message.HeaderInterface;

/**
 * This class is used to create a filter based on the currently selected
 * message (if multiple selected, the first one in the selection array
 * is used) - either using Subject, To or From. 
 * 
 * @author Karl Peder Olesen (karlpeder), 20030620
 */
public class CreateFilterOnMessageCommand extends FolderCommand {

	/** Used for creating a filter based on Subject */
	public static final String FILTER_ON_SUBJECT = "Subject";
	/** Used for creating a filter based on From */
	public static final String FILTER_ON_FROM    = "From";
	/** Used for creating a filter based on To */
	public static final String FILTER_ON_TO      = "To";

	/** Type of filter to create */
	private String filterType;

	/** Filter created */
	private Filter filter = null;
	
	/**
	 * Constructor for CreateFilterOnMessageCommand. Calls super
	 * constructor and saves flag for which kind of filter to
	 * create. Default for filter type is FILTER_ON_SUBJECT.
	 * @param references
	 * @param filterType	Which type of filter to create.
	 * 						Used defined constants
	 */
	public CreateFilterOnMessageCommand(
					DefaultCommandReference[] references,
					String filterType) {
		super(references);
		this.filterType = filterType;
	}

	/**
	 * Displays filter dialog for user modifications after creation
	 * of the filter in execute.
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {
		if (filter != null) {
			FilterDialog dialog = new FilterDialog(filter);
		}
	}

	/**
	 * This method generates filter based on Subject, From or
	 * To (depending on parameter transferred to constructor)
	 * of the currently selected message.
	 * 
	 * @param	worker
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		
		// get references to selected folder and message
		FolderCommandReference[] r = 
				(FolderCommandReference[]) getReferences();
		Object[] uids = r[0].getUids(); // uid for messages to save
		if (uids.length == 0) {
			ColumbaLogger.log.info("No filter created since no message was selected");
			return;	// no message selected.
		}
		Object uid = uids[0];
		Folder srcFolder = (Folder) r[0].getFolder();
		// register for status events
 		((StatusObservableImpl) srcFolder.getObservable()).setWorker(worker);
		
		// get value of Subject, From or To header
		HeaderInterface header = srcFolder.getMessageHeader(uid);
		String headerValue = (String) header.get(filterType);
		
		if (headerValue == null) {
			ColumbaLogger.log.error("Error getting " + filterType + 
					" header. No filter created");
			return;
		}
		
		// create filter
		String descr = filterType + " contains [" + headerValue + "]";
		filter = createFilter(descr, filterType, headerValue);
		
		// add filter to the folders filterlist
		srcFolder.getFilterList().add(filter);
		
	}


	/**
	 * Private utility for creating a filter on a given
	 * headerfield.
	 * The criteria used is "contains" and the action is
	 * set to "Mark as Read".
	 * @param	filterDescr		Name / description to assign to filter
	 * @param	headerField		The header field to base filter on
	 * @param	pattern			The pattern to use in the filter
	 * @return	The filter created
	 */
	public Filter createFilter(String filterDescr,
							   String headerField, 
							   String pattern) {
		// create filter element
		XmlElement filter = new XmlElement("filter");
		filter.addAttribute("description", filterDescr);
		filter.addAttribute("enabled","true");
		XmlElement rules = new XmlElement("rules");
		rules.addAttribute("condition", "matchall");
		
		// create criteria list
		XmlElement criteria = new XmlElement("criteria");
		criteria.addAttribute("type", headerField);
		criteria.addAttribute("headerfield", headerField);
		criteria.addAttribute("criteria", "contains");
		criteria.addAttribute("pattern", pattern);
		rules.addElement(criteria);
		filter.addElement(rules);

		// create action list
		XmlElement actionList = new XmlElement("actionlist");
		XmlElement action = new XmlElement("action");
		action.addAttribute("type","Mark as Read");
		actionList.addElement(action);
		filter.addElement(actionList);

		// return filter based on the XmlElement just created		
		return new Filter(filter);
	}
	
}