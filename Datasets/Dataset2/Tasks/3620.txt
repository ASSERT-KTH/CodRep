ColumbaLogger.log.info("loading new instance =" + type);

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
package org.columba.mail.folder.search;

import org.columba.core.command.StatusObservable;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.core.util.ListTools;

import org.columba.mail.filter.Filter;
import org.columba.mail.filter.FilterCriteria;
import org.columba.mail.filter.FilterRule;
import org.columba.mail.filter.plugins.AbstractFilter;
import org.columba.mail.folder.Folder;
import org.columba.mail.message.ColumbaMessage;
import org.columba.mail.plugin.AbstractFilterPluginHandler;
import org.columba.mail.util.MailResourceLoader;

import java.util.Arrays;
import java.util.Hashtable;
import java.util.LinkedList;
import java.util.List;
import java.util.ListIterator;

import javax.swing.JOptionPane;


/**
 * Divides search requests and passes them along to the
 * optimized {@link QueryEngine} for execution.
 * <p>
 * Search requests which can't be performed by the
 * {@link QueryEngine}, are executed by DefaultSearchEngine
 * using the plugin mechanism.
 *
 * @author tstich, fdietz
 */
public class DefaultSearchEngine {
    public static final int INIT = 0;
    public static final int RANDOM = 1;
    protected static Hashtable filterCache;
    private int mode;
    protected Folder folder;
    private QueryEngine nonDefaultEngine;

    public DefaultSearchEngine(Folder folder) {
        this.folder = folder;

        filterCache = new Hashtable();

        mode = RANDOM;

        nonDefaultEngine = new DummyQueryEngine();
    }

    public StatusObservable getObservable() {
        return folder.getObservable();
    }

    protected synchronized AbstractFilter getFilter(String type) {
        // try to re-use already instanciated class
        if (filterCache.containsKey(type) == true) {
            return (AbstractFilter) filterCache.get(type);
        }

        ColumbaLogger.log.debug("loading new instance =" + type);

        AbstractFilter instance = null;

        try {
            AbstractFilterPluginHandler handler = (AbstractFilterPluginHandler) MainInterface.pluginManager.getHandler(
                    "org.columba.mail.filter");
            instance = (AbstractFilter) handler.getActionPlugin(type, null);
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(null,
                "Error while trying to load filter plugin =" + type);
            ex.printStackTrace();
        }

        if (instance != null) {
            filterCache.put(type, instance);
        }

        return instance;
    }

    protected boolean processRule(Object uid, FilterCriteria criteria,
        String type) throws Exception {
        if (type == null) {
            JOptionPane.showMessageDialog(null,
                "Filter type couldn't been found", "Error occured",
                JOptionPane.ERROR_MESSAGE);

            return false;
        }

        AbstractFilter instance = getFilter(type);

        if (instance == null) {
            return false;
        }

        Object[] args = instance.getAttributes();

        Object[] attributes = new Object[args.length];

        for (int j = 0; j < args.length; j++) {
            attributes[j] = criteria.get((String) args[j]);
        }

        return instance.process(attributes, folder, uid);
    }

    protected List processCriteria(FilterRule rule, List uids)
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

                for (int i = 0; (i < rule.count()) && b; i++) {
                    FilterCriteria criteria = rule.get(i);

                    String type = criteria.getType();

                    b &= processRule(uid, criteria, type);
                }

                if (b) {
                    result.add(uid);
                }
            }
        } else { // MATCH ANY

            while (it.hasNext()) {
                b = false;
                uid = it.next();

                for (int i = 0; (i < rule.count()) && !b; i++) {
                    FilterCriteria criteria = rule.get(i);

                    String type = criteria.getType();

                    b = processRule(uid, criteria, type);
                }

                if (b) {
                    result.add(uid);
                }
            }
        }

        //		result = mergeFilterResult(v, uids, match);
        // only for debugging purpose
        //printList( result );
        return result;
    }

    protected void divideFilterRule(FilterRule filterRule,
        FilterRule notDefaultEngine, FilterRule defaultEngine) {
        FilterCriteria actCriteria;

        String[] caps = getNonDefaultEngine().getCaps();

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

    /**
     * @see org.columba.mail.folder.SearchEngineInterface#searchMessages(org.columba.mail.filter.Filter, java.lang.Object, org.columba.core.command.WorkerStatusController)
     */
    public Object[] searchMessages(Filter filter, Object[] uids)
        throws Exception {
        long startTime = System.currentTimeMillis();

        List notDefaultEngineResult = null;
        List defaultEngineResult = new LinkedList();

        FilterRule filterRule = filter.getFilterRule();

        FilterRule notDefaultEngine = new FilterRule();
        FilterRule defaultEngine = new FilterRule();

        divideFilterRule(filterRule, notDefaultEngine, defaultEngine);

        if (defaultEngine.count() > 0) {
            if (uids != null) {
                defaultEngineResult = queryEngine(defaultEngine, uids);
            } else {
                defaultEngineResult = queryEngine(defaultEngine);
            }
        }

        if (notDefaultEngine.count() == 0) {
            notDefaultEngineResult = defaultEngineResult;
        } else {
            // MATCH_ALL
            if (filterRule.getConditionInt() == FilterRule.MATCH_ALL) {
                if (defaultEngine.count() > 0) {
                    notDefaultEngineResult = processCriteria(notDefaultEngine,
                            defaultEngineResult);
                } else {
                    if (uids != null) {
                        notDefaultEngineResult = processCriteria(notDefaultEngine,
                                Arrays.asList(uids));
                    } else {
                        notDefaultEngineResult = processCriteria(notDefaultEngine,
                                Arrays.asList(folder.getUids()));
                    }
                }
            }
            // MATCH_ANY
            else {
                if (uids != null) {
                    List uidList = new LinkedList(Arrays.asList(uids));
                    ListTools.substract(uidList, defaultEngineResult);

                    notDefaultEngineResult = processCriteria(notDefaultEngine,
                            uidList);

                    notDefaultEngineResult.addAll(defaultEngineResult);
                } else {
                    notDefaultEngineResult = processCriteria(notDefaultEngine,
                            Arrays.asList(folder.getUids()));
                }
            }
        }

        /*
        worker.setDisplayText(
                "Search Result: "
                        + notDefaultEngineResult.size()
                        + " messages found in "
                        + (System.currentTimeMillis() - startTime)
                        + " ms");
        */
        return notDefaultEngineResult.toArray();
    }

    /**
     * @see org.columba.mail.folder.SearchEngineInterface#searchMessages(org.columba.mail.filter.Filter, org.columba.core.command.WorkerStatusController)
     */
    public Object[] searchMessages(Filter filter) throws Exception {
        if (getObservable() != null) {
            getObservable().setMessage(MailResourceLoader.getString(
                    "statusbar", "message", "search"));
        }

        //return searchMessages(filter, null);
        Object[] result = searchMessages(filter, null);

        if (getObservable() != null) {
            // clear status bar message now we are done (with a delay)
            getObservable().clearMessageWithDelay();
        }

        return result;
    }

    /**
             * @see org.columba.mail.folder.DefaultSearchEngine#queryEngine(org.columba.mail.filter.FilterRule, java.lang.Object, org.columba.core.command.WorkerStatusController)
             */
    protected List queryEngine(FilterRule filter, Object[] uids)
        throws Exception {
        return processCriteria(filter, Arrays.asList(uids));
    }

    /**
     * @see org.columba.mail.folder.DefaultSearchEngine#queryEngine(org.columba.mail.filter.FilterRule, org.columba.core.command.WorkerStatusController)
     */
    protected List queryEngine(FilterRule filter) throws Exception {
        Object[] uids = folder.getUids();

        return processCriteria(filter, Arrays.asList(uids));
    }

    /**
     * @return
     */
    public QueryEngine getNonDefaultEngine() {
        return nonDefaultEngine;
    }

    /**
     * @param engine
     */
    public void setNonDefaultEngine(QueryEngine engine) {
        nonDefaultEngine = engine;
    }

    public void messageAdded(ColumbaMessage message) throws Exception {
        getNonDefaultEngine().messageAdded(message);
    }

    public void messageRemoved(Object uid) throws Exception {
        getNonDefaultEngine().messageRemoved(uid);
    }

    public void sync() throws Exception {
        getNonDefaultEngine().sync();
    }
}