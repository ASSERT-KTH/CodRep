dialog.showDialog("Error while trying to instantiate plugin " +

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.core.plugin;

import org.columba.core.gui.util.ExceptionDialog;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.loader.DefaultClassLoader;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.core.xml.XmlElement;

import java.io.File;

import java.lang.reflect.InvocationTargetException;

import java.util.HashMap;
import java.util.Hashtable;
import java.util.List;
import java.util.ListIterator;
import java.util.Map;
import java.util.Vector;


/**
 *
 *
 *
 * Every entrypoint is represented by this abstract handler class
 * <p>
 * We use the Strategy Pattern here.
 * <p>
 * The <class>AbstractPluginHandler</class> is the Context of the Strategy
 * pattern.
 * <p>
 * The plugins (<interface>PluginInterface</interface>) represent the used
 * strategy.
 * <p>
 * Therefore, the context is responsible to set the appropriate strategy we
 * use.
 * <p>
 * In other words the plugin handler decides which plugin should be executed
 * and returns an instance of the plugin class.
 * <p>
 *
 * example of loading a plugin: <code>
 *
 * ActionPluginHandler handler = (ActionPluginHandler)
 *           MainInterface.pluginManager.getHandler("org.columba.core.action");
 *
 * Object[] parameter = { myparam };
 *
 * Action action = handler.getPlugin("MoveAction", parameter);
 * </code>
 * <p>
 * Please read the documentation of the corresponding methods for more details.
 *
 * @author fdietz
 *
 */
public abstract class AbstractPluginHandler implements PluginHandlerInterface {
    protected String id;
    protected XmlElement parentNode;
    protected PluginListConfig pluginListConfig;
    protected PluginManager pluginManager;

    //	translate plugin-id to user-visible name
    //  example: org.columba.example.HelloWorld$HelloPlugin -> HelloWorld
    protected Hashtable transformationTable;

    /**
     * associate extension with plugin which owns the extension
     */
    protected Map pluginMap;
    protected List externalPlugins;

    /**
     * @param id
     * @param config
     */
    public AbstractPluginHandler(String id, String config) {
        super();
        this.id = id;
        transformationTable = new Hashtable();

        if (config != null) {
            pluginListConfig = new PluginListConfig(config);
        }

        externalPlugins = new Vector();

        pluginMap = new HashMap();

        ColumbaLogger.log.info("initialising plugin-handler: " + id);
    }

    /**
     * @return
     */
    protected PluginListConfig getConfig() {
        return pluginListConfig;
    }

    /**
     * @return
     */
    public String getId() {
        return id;
    }

    /**
     *
     * Returns an instance of the plugin
     *
     * example plugin constructor:
     *
     * public Action(JFrame frame, String text) { .. do anything .. }
     *
     * --> arguments:
     *
     * Object[] args = { frame, text };
     *
     * @param name
     *            name of plugin
     * @param args
     *            constructor arguments needed to instanciate the plugin
     * @return instance of plugin class
     *
     * @throws Exception
     */
    public Object getPlugin(String name, Object[] args)
        throws Exception {
        ColumbaLogger.log.info("name=" + name);
        ColumbaLogger.log.info("arguments=" + args);

        String className = getPluginClassName(name, "class");
        ColumbaLogger.log.info("class=" + className);

        if (className == null) {
            if (MainInterface.DEBUG) {
                XmlElement.printNode(parentNode, " ");
            }

            // if className isn't specified show error dialog
            NotifyDialog dialog = new NotifyDialog();
            dialog.showDialog("Error while trying to instanciate plugin " +
                name +
                ".\n Classname wasn't found. This probably means that plugin.xml is broken or incomplete.");

            return null;
        }

        return getPlugin(name, className, args);
    }

    /**
     * @param name
     * @param className
     * @param args
     * @return @throws
     *         Exception
     */
    protected Object getPlugin(String name, String className, Object[] args)
        throws Exception {
        try {
            return loadPlugin(className, args);
        } catch (ClassNotFoundException ex) {
            ex.printStackTrace();

            /*
            int dollarLoc = name.indexOf('$');
            String pluginId =
                    (dollarLoc > 0 ? name.substring(0, dollarLoc) : name);
            */

            // get plugin id 
            String pluginId = (String) pluginMap.get(name);

            // get runtime properties
            String type = pluginManager.getPluginType(pluginId);
            File pluginDir = pluginManager.getJarFile(pluginId);

            return PluginLoader.loadExternalPlugin(className, type, pluginDir,
                args);
        } catch (InvocationTargetException ex) {
            ExceptionDialog d = new ExceptionDialog();
            d.showDialog(ex.getTargetException());
            ex.getTargetException().printStackTrace();
            throw ex;
        }
    }

    /**
     * @param name
     *            example: "org.columba.example.TextPlugin"
     * @param id
     *            this is usually just "class"
     * @return
     */
    protected String getPluginClassName(String name, String id) {
        int count = parentNode.count();

        for (int i = 0; i < count; i++) {
            XmlElement action = parentNode.getElement(i);

            String s = action.getAttribute("name");

            /*
             * if (transformationTable.contains(id)) { // this is an external
             * plugin
             *  // -> extract the correct id // example original id:
             * org.columba.mail.SpamAssassin$spamassassin // example result:
             * spamassassin
             *
             * s = s.substring(s.indexOf('$'));
             * System.out.println("class-id="+s); }
             */

            // FIXME

            /*
            if (s.indexOf('$') != -1) {
                    // this is an external plugin
                    // -> extract the correct id
                    s = s.substring(s.indexOf('$')+1);
                    System.out.println("class-id="+s);
            }
            */
            if (name.equals(s)) {
                String clazz = action.getAttribute(id);

                return clazz;
            }
        }

        return null;
    }

    /**
     *
     * return value of xml attribute of specific plugin
     *
     * @param name
     *            name of plugin
     * @param attribute
     *            key of xml attribute
     * @return value of xml attribute
     */
    public String getAttribute(String name, String attribute) {
        int count = parentNode.count();

        for (int i = 0; i < count; i++) {
            XmlElement action = parentNode.getElement(i);

            String s = action.getAttribute("name");

            // return if attribute was not found
            if (s == null) {
                return null;
            }

            /*
            if (s.indexOf('$') != -1) {
                    // this is an external plugin
                    // -> extract the correct id
                    s = s.substring(0, s.indexOf('$'));

            }
            */
            if (name.equals(s)) {
                String value = action.getAttribute(attribute);

                return value;
            }
        }

        return null;
    }

    /**
     * Return array of enabled plugins.
     *
     * @return array of enabled plugins
     */
    public String[] getPluginIdList() {
        int count = parentNode.count();

        //String[] list = new String[count];
        List list = new Vector();

        for (int i = 0; i < count; i++) {
            XmlElement action = parentNode.getElement(i);
            String s = action.getAttribute("name");

            XmlElement element = MainInterface.pluginManager.getPluginElement(s);

            if (element == null) {
                // this is no external plugin
                // -> just add it to the list
                list.add(s);

                continue;
            }

            String enabled = element.getAttribute("enabled");

            if (enabled == null) {
                enabled = "true";
            }

            boolean e = Boolean.valueOf(enabled).booleanValue();

            if (e) {
                list.add(s);
            }

            //list[i] = s;
        }

        String[] strs = new String[list.size()];

        for (int i = 0; i < list.size(); i++) {
            strs[i] = (String) list.get(i);
        }

        //return list;
        return strs;
    }

    public boolean exists(String id) {
        ColumbaLogger.log.info("id=" + id);

        String[] list = getPluginIdList();

        for (int i = 0; i < list.length; i++) {
            String plugin = list[i];
            String searchId = plugin;

            /*
            int index = plugin.indexOf("$");
            String searchId;
            if (index != -1)
                    searchId = plugin.substring(0, plugin.indexOf("$"));
            else
                    searchId = plugin;
            */
            ColumbaLogger.log.info(" - plugin id=" + plugin);
            ColumbaLogger.log.info(" - search id=" + searchId);

            if (searchId.equals(id)) {
                return true;
            }
        }

        return false;
    }

    public ListIterator getExternalPlugins() {
        return externalPlugins.listIterator();
    }

    /**
     * @return
     */
    public PluginManager getPluginManager() {
        return pluginManager;
    }

    /**
     * @param className
     * @param args
     * @return @throws
     *         Exception
     */
    protected Object loadPlugin(String className, Object[] args)
        throws Exception {
        return new DefaultClassLoader().instanciate(className, args);
    }

    /**
     * @param pluginManager
     */
    public void setPluginManager(PluginManager pluginManager) {
        this.pluginManager = pluginManager;
    }

    public String getUserVisibleName(String id) {
        // this is no external plugin
        //  -> just return the name
        if (id.indexOf('$') == -1) {
            return id;
        }

        //String pluginId = id.substring(0, id.indexOf('$'));
        //String name = id.substring(id.indexOf('$'), id.length() - 1);
        int count = parentNode.count();

        for (int i = 0; i < count; i++) {
            XmlElement action = parentNode.getElement(i);
            String s = action.getAttribute("name");
            String s2 = action.getAttribute("uservisiblename");

            if (id.equals(s)) {
                return s2;
            }
        }

        return null;
    }

    /**
     * Register plugin at this extension point.
     *
     * @param id
     * @param extension
     */
    public void addExtension(String id, XmlElement extension) {
        // add external plugin to list
        // --> this is used to distinguish internal/external plugins
        externalPlugins.add(id);

        ListIterator iterator = extension.getElements().listIterator();
        XmlElement action;

        while (iterator.hasNext()) {
            action = (XmlElement) iterator.next();
            action.addAttribute("uservisiblename", action.getAttribute("name"));

            // associate extension with plugin which owns the extension
            pluginMap.put(action.getAttribute("name"), id);

            /*
            String newName = id + '$' + action.getAttribute("name");
            String userVisibleName = action.getAttribute("name");

            // associate id with newName for later reference
            transformationTable.put(id, newName);

            action.addAttribute("name", newName);
            action.addAttribute("uservisiblename", userVisibleName);
            */
            parentNode.addElement(action);
        }
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.core.plugin.PluginHandlerInterface#getParent()
     */
    public XmlElement getParent() {
        return parentNode;
    }
}