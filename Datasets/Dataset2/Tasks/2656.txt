Header header = folder.getHeaderFields(uid, new String[] {"To", "Cc"});

package org.columba.mail.filter.plugins;

import org.columba.core.command.WorkerStatusController;
import org.columba.mail.filter.FilterCriteria;
import org.columba.mail.folder.Folder;
import org.columba.mail.message.ColumbaHeader;

/**
 * @author freddy
 *
 * This FilterPlugin searches every To and Cc headerfield
 * of an occurence of a search string and combines the result
 * with an logical OR operation
 * 
 */
public class ToOrCcFilter extends HeaderfieldFilter {

	/**
	 * Constructor for ToOrCcFilter.
	 */
	public ToOrCcFilter() {
		super();
	}

	/**
	 * 
	 * we need the criteria attribute, which can be "contains" or "contains not"
	 * 
	 * "pattern" is our search string
	 * 
	 * @see org.columba.mail.filter.plugins.AbstractFilter#getAttributes()
	 */
	public Object[] getAttributes() {
		Object[] args = { "criteria", "pattern" };

		return args;
	}

	/**
	 * @see org.columba.mail.filter.plugins.AbstractFilter#process(java.lang.Object, org.columba.mail.folder.Folder, java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public boolean process(
		Object[] args,
		Folder folder,
		Object uid)
		throws Exception {

		// get the header of the message
		ColumbaHeader header = folder.getMessageHeader(uid);
		if ( header == null ) return false;
		
		// convert the condition string to an int which is easier to handle
		int condition = FilterCriteria.getCriteria((String) args[0]);
		// the search pattern
		String pattern = (String) args[1];

		// get the "To" headerfield from the header
		String to = (String) header.get("To");
		// get the "Cc" headerfield from the header
		String cc = (String) header.get("Cc");
			
		// test if our To headerfield contains or contains not the search string	
		boolean result = match(to, condition, pattern);
		// do the same for the Cc headerfield and OR the results
		result |= match(cc, condition, pattern);
		// return the result as boolean value true or false
		return result;
	}

	
}