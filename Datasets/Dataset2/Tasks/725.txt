rootFolder = (IMAPRootFolder) ((IMAPFolder) folder).getRootFolder();

package org.columba.mail.folder;

import java.util.Date;
import java.util.Vector;

import org.columba.core.command.WorkerStatusController;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.filter.Filter;
import org.columba.mail.filter.FilterCriteria;
import org.columba.mail.filter.FilterRule;
import org.columba.mail.folder.imap.IMAPFolder;
import org.columba.mail.folder.imap.IMAPRootFolder;
import org.columba.mail.imap.parser.MessageSet;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class RemoteSearchEngine implements SearchEngineInterface {

	//protected IMAPProtocol imap;

	protected Folder folder;
	protected IMAPRootFolder rootFolder;

	public RemoteSearchEngine(Folder folder) {
		this.folder = folder;

		rootFolder = ((IMAPFolder) folder).getImapRootFolder();
		//imap = rootFolder.getImapServerConnection();

	}

	protected String createSubjectString(FilterCriteria criteria) {
		StringBuffer searchString = new StringBuffer();

		// we need to append "NOT"
		if (criteria.getCriteria() == FilterCriteria.CONTAINS_NOT)
			searchString.append("NOT ");

		searchString.append("SUBJECT ");

		searchString.append(criteria.getPattern());

		return searchString.toString();
	}

	protected String createToString(FilterCriteria criteria) {
		StringBuffer searchString = new StringBuffer();

		// we need to append "NOT"
		if (criteria.getCriteria() == FilterCriteria.CONTAINS_NOT)
			searchString.append("NOT ");

		searchString.append("TO ");

		searchString.append(criteria.getPattern());

		return searchString.toString();
	}

	protected String createCcString(FilterCriteria criteria) {
		StringBuffer searchString = new StringBuffer();

		// we need to append "NOT"
		if (criteria.getCriteria() == FilterCriteria.CONTAINS_NOT)
			searchString.append("NOT ");

		searchString.append("CC ");

		searchString.append(criteria.getPattern());

		return searchString.toString();
	}

	protected String createBccString(FilterCriteria criteria) {
		StringBuffer searchString = new StringBuffer();

		// we need to append "NOT"
		if (criteria.getCriteria() == FilterCriteria.CONTAINS_NOT)
			searchString.append("NOT ");

		searchString.append("BCC ");

		searchString.append(criteria.getPattern());

		return searchString.toString();
	}

	protected String createFromString(FilterCriteria criteria) {
		StringBuffer searchString = new StringBuffer();

		// we need to append "NOT"
		if (criteria.getCriteria() == FilterCriteria.CONTAINS_NOT)
			searchString.append("NOT ");

		searchString.append("FROM ");

		searchString.append(criteria.getPattern());

		return searchString.toString();
	}

	protected String createToCCString(FilterCriteria criteria) {
		StringBuffer searchString = new StringBuffer();

		// we need to append "NOT"
		if (criteria.getCriteria() == FilterCriteria.CONTAINS_NOT)
			searchString.append("NOT ");
	
		searchString.append("OR ");

		searchString.append("TO ");

		searchString.append(criteria.getPattern());
		
		searchString.append("CC ");

		searchString.append(criteria.getPattern());

		return searchString.toString();
	}

	protected String createBodyString(FilterCriteria criteria) {
		StringBuffer searchString = new StringBuffer();

		// we need to append "NOT"
		if (criteria.getCriteria() == FilterCriteria.CONTAINS_NOT)
			searchString.append("NOT ");

		searchString.append("BODY ");

		searchString.append(criteria.getPattern());

		return searchString.toString();
	}

	protected String createSizeString(FilterCriteria criteria) {
		StringBuffer searchString = new StringBuffer();

		if (criteria.getCriteria() == FilterCriteria.SIZE_BIGGER)
			searchString.append("LARGER ");
		else
			searchString.append("SMALLER ");

		searchString.append(criteria.getPattern());

		return searchString.toString();
	}

	protected String createDateString(FilterCriteria criteria) {
		StringBuffer searchString = new StringBuffer();

		if (criteria.getCriteria() == FilterCriteria.DATE_BEFORE)
			searchString.append("SENTBEFORE ");
		else
			searchString.append("SENTAFTER ");

		searchString.append(criteria.getPattern());

		return searchString.toString();
	}

	protected String createFlagsString(FilterCriteria criteria) {
		StringBuffer searchString = new StringBuffer();

		// we need to append "NOT"
		if (criteria.getCriteria() == FilterCriteria.CONTAINS_NOT)
			searchString.append("NOT ");

		String headerField = criteria.getPattern();

		if (headerField.equalsIgnoreCase("Answered")) {
			searchString.append("ANSWERED ");
		} else if (headerField.equalsIgnoreCase("Deleted")) {
			searchString.append("DELETED ");
		} else if (headerField.equalsIgnoreCase("Flagged")) {
			searchString.append("FLAGGED ");
		} else if (headerField.equalsIgnoreCase("Recent")) {
			searchString.append("NEW ");
		} else if (headerField.equalsIgnoreCase("Draft")) {
			searchString.append("DRAFT ");
		} else if (headerField.equalsIgnoreCase("Seen")) {
			searchString.append("SEEN ");
		}

		return searchString.toString();
	}

	protected String createPriorityString(FilterCriteria criteria) {
		StringBuffer searchString = new StringBuffer();

		// we need to append "NOT"
		if (criteria.getCriteria() == FilterCriteria.CONTAINS_NOT)
			searchString.append("NOT ");

		searchString.append("X-Priority ");

		Integer searchPattern = null;
		String pattern = criteria.getPattern();
		if (pattern.equalsIgnoreCase("Highest")) {
			searchPattern = new Integer(1);
		} else if (pattern.equalsIgnoreCase("High")) {
			searchPattern = new Integer(2);
		} else if (pattern.equalsIgnoreCase("Normal")) {
			searchPattern = new Integer(3);
		} else if (pattern.equalsIgnoreCase("Low")) {
			searchPattern = new Integer(4);
		} else if (pattern.equalsIgnoreCase("Lowest")) {
			searchPattern = new Integer(5);
		}
		searchString.append(searchPattern.toString());

		return searchString.toString();
	}

	protected String generateSearchString(
		FilterRule rule,
		Vector ruleStringList) {
		StringBuffer searchString = new StringBuffer();

		if (rule.count() > 1) {

			int condition = rule.getConditionInt();
			String conditionString;
			if (condition == FilterRule.MATCH_ALL) {
				// match all
				conditionString = "OR";

			} else {
				// match any
				conditionString = "AND";
			}

			// concatenate all criteria together
			//  -> create one search-request string
			for (int i = 0; i < rule.count(); i++) {

				if (i != rule.count() - 1)
					searchString.append(conditionString + " ");

				searchString.append((String) ruleStringList.get(i));

				if (i != rule.count() - 1)
					searchString.append(" ");

			}
		} else {
			searchString.append((String) ruleStringList.get(0));
		}

		return searchString.toString();
	}
	
	protected String generateSearchString( Filter filter )
	{
		FilterRule rule = filter.getFilterRule();

		Vector ruleStringList = new Vector();

		for (int i = 0; i < rule.count(); i++) {
			FilterCriteria criteria = rule.getCriteria(i);
			String headerItem;
			//StringBuffer searchString = new StringBuffer();
			String searchString = null;

			switch (criteria.getHeaderItem()) {
				case FilterCriteria.SUBJECT :
					{
						searchString = createSubjectString(criteria);

						break;
					}
				case FilterCriteria.TO :
					{
						searchString = createToString(criteria);
						break;
					}
				case FilterCriteria.FROM :
					{
						searchString = createFromString(criteria);
						break;
					}
				case FilterCriteria.CC :
					{
						searchString = createCcString(criteria);
						break;
					}
				case FilterCriteria.BCC :
					{
						searchString = createBccString(criteria);
						break;
					}
				case FilterCriteria.TO_CC :
					{
						searchString = createToString(criteria);

						break;
					}
				case FilterCriteria.BODY :
					{
						searchString = createBodyString(criteria);
						break;
					}
				case FilterCriteria.SIZE :
					{
						searchString = createSizeString(criteria);

						break;
					}
				case FilterCriteria.DATE :
					{
						searchString = createDateString(criteria);

						break;
					}
				case FilterCriteria.FLAGS :
					{
						searchString = createFlagsString(criteria);

						break;
					}
				case FilterCriteria.PRIORITY :
					{
						searchString = createPriorityString(criteria);

						break;
					}

			}
			ruleStringList.add(searchString.toString());
		}

		String searchString = generateSearchString(rule, ruleStringList);

		/*
		if (searchString.length() == 0)
			searchString =
				"1:* OR HEADER SUBJECT test OR HEADER FROM fdietz@gmx.de HEADER FROM freddy@uni-mannheim.de";
		*/
		
		
		ColumbaLogger.log.info("searchString=" + searchString.toString());
		
		return searchString;
	}
	
	public Object[] searchMessages(
		Filter filter,
		WorkerStatusController worker)
		throws Exception
		{
			return ((IMAPFolder) folder)
			.getStore()
			.search(generateSearchString( filter) , ((IMAPFolder) folder).getImapPath(), worker)
			.toArray();
		}

	public Object[] searchMessages(
		Filter filter,
		Object[] uids,
		WorkerStatusController worker)
		throws Exception {
		

		return ((IMAPFolder) folder)
			.getStore()
			.search(uids, generateSearchString( filter), ((IMAPFolder) folder).getImapPath(), worker)
			.toArray();

	}

}