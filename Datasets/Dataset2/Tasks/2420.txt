"org.columba.mail.filter");

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
package org.columba.mail.folder;

import java.util.Arrays;
import java.util.Hashtable;
import java.util.LinkedList;
import java.util.List;
import java.util.ListIterator;

import javax.swing.JOptionPane;

import org.columba.core.command.WorkerStatusController;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.core.util.ListTools;
import org.columba.mail.filter.Filter;
import org.columba.mail.filter.FilterCriteria;
import org.columba.mail.filter.FilterRule;
import org.columba.mail.filter.plugins.AbstractFilter;
import org.columba.mail.message.AbstractMessage;
import org.columba.mail.plugin.AbstractFilterPluginHandler;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public abstract class AbstractSearchEngine {

	public AbstractSearchEngine(Folder folder) {
		this.folder = folder;

		filterCache = new Hashtable();
	}

	public void messageAdded(AbstractMessage message) throws Exception {
	};

	public void messageRemoved(Object uid) throws Exception {
	};

	public void reset() throws Exception {
	};

	protected synchronized AbstractFilter getFilter(String type) {

		ColumbaLogger.log.debug(
			"trying to re-use cached instanciation =" + type);

		// try to re-use already instanciated class
		if (filterCache.containsKey(type) == true)
			return (AbstractFilter) filterCache.get(type);

		ColumbaLogger.log.debug("loading new instance =" + type);

		AbstractFilter instance = null;
		try {
			AbstractFilterPluginHandler handler =
				(
					AbstractFilterPluginHandler) MainInterface
						.pluginManager
						.getHandler(
					"filter");
			instance = (AbstractFilter) handler.getActionPlugin(type, null);
		} catch (Exception ex) {
			JOptionPane.showMessageDialog(
				null,
				"Error while trying to load filter plugin =" + type);
			ex.printStackTrace();
		}

		if (instance != null)
			filterCache.put(type, instance);

		return instance;

	}

	protected boolean processRule(
		Object uid,
		WorkerStatusController worker,
		FilterCriteria criteria,
		String type)
		throws Exception {
		if (type == null) {
			JOptionPane.showMessageDialog(
				null,
				"Filter type couldn't been found",
				"Error occured",
				JOptionPane.ERROR_MESSAGE);
			return false;
		}

		AbstractFilter instance = getFilter(type);

		if (instance == null)
			return false;

		Object[] args = instance.getAttributes();

		Object[] attributes = new Object[args.length];
		for (int j = 0; j < args.length; j++) {
			attributes[j] = criteria.get((String) args[j]);
		}

		boolean b = instance.process(attributes, folder, uid, worker);
		return b;
	}

	protected LinkedList processCriteria(
		FilterRule rule,
		List uids,
		WorkerStatusController worker)
		throws Exception {

		LinkedList result = new LinkedList();
		boolean b;

		int match = rule.getConditionInt();

		ListIterator it = uids.listIterator();

		Object uid;

		// MATCH_ALL
		if (match == FilterRule.MATCH_ALL) {
			while (it.hasNext()) {

				b = true;
				uid = it.next();

				for (int i = 0;(i < rule.count()) && b; i++) {
					FilterCriteria criteria = rule.get(i);

					String type = criteria.getType();

					AbstractFilter instance;
					b &= processRule(uid, worker, criteria, type);
				}

				if (b)
					result.add(uid);
			}
		}
		// MATCH_ANY
		else {
			while (it.hasNext()) {

				b = false;
				uid = it.next();

				for (int i = 0;(i < rule.count()) && !b; i++) {
					FilterCriteria criteria = rule.get(i);

					String type = criteria.getType();

					AbstractFilter instance;
					b = processRule(uid, worker, criteria, type);
				}

				if (b)
					result.add(uid);
			}
		}

		//		result = mergeFilterResult(v, uids, match);

		// only for debugging purpose
		//printList( result );

		return result;
		/*
		String pattern = criteria.getPattern();
		//String condition = criteria.getCriteria();
		int condition = criteria.getCriteria();
		
		//System.out.println("i="+i+ " - type="+ type );
		
		if (type.equalsIgnoreCase("Custom Headerfield")) {
			String headerField = criteria.getHeaderItemString();
		
			v =
				processHeaderCriteria(
					uids,
					headerField,
					pattern,
					condition,
					worker);
		
			//printList( v );
		} else if (type.equalsIgnoreCase("To or Cc")) {
			Vector v1 =
				processHeaderCriteria(
					uids,
					"To",
					pattern,
					condition,
					worker);
			Vector v2 =
				processHeaderCriteria(
					uids,
					"Cc",
					pattern,
					condition,
					worker);
		
			v = mergeLists(v1, v2);
		} else if (type.equalsIgnoreCase("Date")) {
			v = processDateCriteria(uids, pattern, condition, worker);
		} else if (type.equalsIgnoreCase("Size")) {
			v = processSizeCriteria(uids, pattern, condition, worker);
		} else if (type.equalsIgnoreCase("Flags")) {
			v = processFlagsCriteria(uids, pattern, condition, worker);
		} else if (type.equalsIgnoreCase("Priority")) {
			v = processPriorityCriteria(uids, pattern, condition, worker);
		} else if (type.equalsIgnoreCase("Body")) {
			v = processBodyCriteria(uids, pattern, condition, worker);
		} else {
			v =
				processHeaderCriteria(
					uids,
					type,
					pattern,
					condition,
					worker);
			//printList( v );
		}
		
		
		list.add(v);
		}
		*/

	}

	protected Folder folder;

	protected static Hashtable filterCache;

	public abstract String[] getCaps();

	protected void divideFilterRule(
		FilterRule filterRule,
		FilterRule notDefaultEngine,
		FilterRule defaultEngine) {

		FilterCriteria actCriteria;

		String[] caps = getCaps();

		List capList = Arrays.asList(caps);

		notDefaultEngine.setCondition(filterRule.getCondition());
		defaultEngine.setCondition(filterRule.getCondition());

		for (int i = 0; i < filterRule.count(); i++) {
			actCriteria = filterRule.get(i);
			if (capList.contains(actCriteria.getType())) {
				defaultEngine.add(actCriteria);
			} else {
				notDefaultEngine.add(actCriteria);
			}
		}
	}

	protected abstract LinkedList queryEngine(
		FilterRule filter,
		WorkerStatusController worker)
		throws Exception;

	protected abstract LinkedList queryEngine(
		FilterRule filter,
		Object[] uids,
		WorkerStatusController worker)
		throws Exception;

	/**
	 * @see org.columba.mail.folder.SearchEngineInterface#searchMessages(org.columba.mail.filter.Filter, java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public Object[] searchMessages(
		Filter filter,
		Object[] uids,
		WorkerStatusController worker)
		throws Exception {
			
			long startTime = System.currentTimeMillis();

		LinkedList notDefaultEngineResult = null;
		LinkedList defaultEngineResult = new LinkedList();

		FilterRule filterRule = filter.getFilterRule();

		FilterRule notDefaultEngine = new FilterRule();
		FilterRule defaultEngine = new FilterRule();

		divideFilterRule(filterRule, notDefaultEngine, defaultEngine);

		if (defaultEngine.count() > 0) {
			if (uids != null)
				defaultEngineResult = queryEngine(defaultEngine, uids, worker);
			else
				defaultEngineResult = queryEngine(defaultEngine, worker);
		}

		if (notDefaultEngine.count() == 0) {
			notDefaultEngineResult = defaultEngineResult;
		} else {

			// MATCH_ALL
			if (filterRule.getConditionInt() == FilterRule.MATCH_ALL) {
				if (defaultEngine.count() > 0)
					notDefaultEngineResult =
						processCriteria(
							notDefaultEngine,
							defaultEngineResult,
							worker);
				else {
					if (uids != null) {
						notDefaultEngineResult =
							processCriteria(
								notDefaultEngine,
								Arrays.asList(uids),
								worker);
					} else {
						notDefaultEngineResult =
							processCriteria(
								notDefaultEngine,
								Arrays.asList(folder.getUids(worker)),
								worker);
					}
				}
			}
			// MATCH_ANY
			else {
				if (uids != null) {
					List uidList = new LinkedList(Arrays.asList(uids));
					ListTools.substract(uidList, defaultEngineResult);

					notDefaultEngineResult =
						processCriteria(notDefaultEngine, uidList, worker);

					notDefaultEngineResult.addAll(defaultEngineResult);
				} else {
					notDefaultEngineResult =
						processCriteria(
							notDefaultEngine,
							Arrays.asList(folder.getUids(worker)),
							worker);
				}

			}
		}
		
		worker.setDisplayText("Search Result: "+notDefaultEngineResult.size()+" messages found in " + (System.currentTimeMillis()-startTime) + " ms" );

		return notDefaultEngineResult.toArray();
	}

	/**
	 * @see org.columba.mail.folder.SearchEngineInterface#searchMessages(org.columba.mail.filter.Filter, org.columba.core.command.WorkerStatusController)
	 */
	public Object[] searchMessages(
		Filter filter,
		WorkerStatusController worker)
		throws Exception {

		return searchMessages(filter, null, worker);
	}

}