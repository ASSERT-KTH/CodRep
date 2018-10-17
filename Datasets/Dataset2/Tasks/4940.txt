import org.columba.ristretto.message.HeaderInterface;

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
package org.columba.mail.filter.plugins;

import java.util.Date;

import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.filter.FilterCriteria;
import org.columba.mail.folder.Folder;
import org.columba.mail.message.HeaderInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class DateFilter extends AbstractFilter {

	/**
	 * Constructor for DateFilter.
	 */
	public DateFilter() {
		super();

	}

	/**
	 * @see org.columba.mail.filter.plugins.AbstractFilter#getAttributes()
	 */
	public Object[] getAttributes() {
		Object[] args = { "criteria", "pattern" };

		return args;
	}

	protected Date transformDate(String pattern) {
		java.text.DateFormat df = java.text.DateFormat.getDateInstance();
		Date searchPattern = null;
		try {
			searchPattern = df.parse(pattern);
		} catch (java.text.ParseException ex) {
			System.out.println("exception: " + ex.getMessage());
			ex.printStackTrace();

			//return new Vector();
		}
		return searchPattern;
	}

	/**
	 * @see org.columba.mail.filter.plugins.AbstractFilter#process(java.lang.Object, org.columba.mail.folder.Folder, java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public boolean process(
		Object[] args,
		Folder folder,
		Object uid)
		throws Exception {
		HeaderInterface header = folder.getMessageHeader(uid);

		int condition = FilterCriteria.getCriteria((String) args[0]);
		Date date = transformDate((String) args[1]);

		boolean result = false;

		//((Rfc822Header) header).printDebug();

		Date d = (Date) header.get("columba.date");
		
		if (d == null)
		{
			ColumbaLogger.log.error("field date not found");
			return false;
		}

		switch (condition) {
			case FilterCriteria.DATE_BEFORE :
				{
					if (d.before(date))
						result = true;
					break;
				}
			case FilterCriteria.DATE_AFTER :
				{
					if (d.after(date))
						result = true;
					break;
				}
		}

		return result;
	}

}