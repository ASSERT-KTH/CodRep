if( multiRMI || true ) {

/*
 * @(#) CarolConfiguration.java	1.0 02/07/15
 *
 * Copyright (C) 2002 - INRIA (www.inria.fr)
 *
 * CAROL: Common Architecture for RMI ObjectWeb Layer
 *
 * This library is developed inside the ObjectWeb Consortium,
 * http://www.objectweb.org
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or any later version.
 * 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
 * USA
 * 
 *
 */
package org.objectweb.carol.util.configuration;

//java import 
import java.io.InputStream;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Locale;
import java.util.Properties;
import java.util.ResourceBundle;
import java.util.StringTokenizer;
import java.util.TreeMap;

import org.objectweb.carol.jndi.ns.NameServiceException;
import org.objectweb.carol.jndi.ns.NameServiceManager;
import org.objectweb.util.monolog.api.LoggerFactory;

/*
 * Interface <code>CarolConfiguration</code> for Carol environment
 * You must have a communication.xml and communication.dtd in your 
 * classpath for the definition of this context
 */

public class CarolConfiguration {

    /**
     * boolean true if the protocol context where load from thefile
     */
    private static boolean configurationLoaded = false;

    /**
     * boolean to start name server need to launch
     */
    private static boolean startNS;
    /**
     * boolean to start carol rmi
     */
    private static boolean startRMI;
    /**
     * boolean to start carol jndi
     */
    private static boolean startJNDI;

    /**
     * defaults carol properties
     */
    private static Properties defaultsProps = null;

    /**
     * carol properties
     */
    private static Properties carolProps = null;

    /**
     * jndi properties
     */
    private static Properties jndiProps = null;

    /**
     * String of the actvated RMI
     */
    private static String protocols;

    /**
     * Boolean for multi RMI
     */
    private static boolean multiRMI;

    /** 
     * Protocol environement hashtable, all rmi Configuration 
     * are classified by there architecture name (jrmp, iiop, ...)
     */
    private static Hashtable rmiConfigurationTable = new Hashtable();

    /**
     * defaultProtocol
     */
    private static String defaultRMI = null;

    /**
     * jndi name of the Protocol
     */
    private static String jndiRMIName = null;

    /**
     * carol defaults properties file name 
     */
    public static final String DEFAULTS_FILE_NAME = "carol-defaults.properties";

    /**
     * rmi properties file name 
     */
    public static final String CAROL_FILE_NAME = "carol.properties";

    /**
     * jndi properties file name
     */
    public static final String JNDI_FILE_NAME = "jndi.properties";

	/**
	  * init the Carol configuration,
	  * A server can call this static method
	  * for instantiate the carol communication layer
	  */
	 public static void init() throws RMIConfigurationException {
		 new CarolConfiguration();
	 }
	 
	/**
	  * init the Carol configuration,
	  * A server can call this static method
	  * for instantiate the carol communication layer
	  */
	 public static void init(LoggerFactory lf) throws RMIConfigurationException {
		 // init Trace 
		 TraceCarol.configure(lf);
		 new CarolConfiguration();
	 }

    /**
     * Constructor 
     * Read the communication context
     */
    public CarolConfiguration() throws RMIConfigurationException {
        if (!configurationLoaded) {
            loadCarolConfiguration();
        }
    }

    /**
     * Get a RMI environment with his architecture name 
     * @return RMIConfiguration the environment, null if not existe
     */
    public static RMIConfiguration getRMIConfiguration(String name) throws RMIConfigurationException {
        if (configurationLoaded) {
            return (RMIConfiguration) rmiConfigurationTable.get(name);
        } else {
            loadCarolConfiguration();
            return (RMIConfiguration) rmiConfigurationTable.get(name);
        }
    }

    /**
     * Get all RMI environment
     * @return Hashtable the rmi configuration hashtable 
     */
    public static Hashtable getAllRMIConfiguration() throws RMIConfigurationException {
        if (configurationLoaded) {
            return rmiConfigurationTable;
        } else {
            loadCarolConfiguration();
            return rmiConfigurationTable;
        }
    }
    /**
     * Get the default rmi
     * @return RMIConfiguration default RMI  Configuration
     */
    public static RMIConfiguration getDefaultProtocol() throws RMIConfigurationException {
        if (configurationLoaded) {
            return (RMIConfiguration) rmiConfigurationTable.get(defaultRMI);
        } else {
            loadCarolConfiguration();
            return (RMIConfiguration) rmiConfigurationTable.get(defaultRMI);
        }
    }

    /**
     * This method read all the the orbX.properties, jndiX.properties file
     * for protocols configurations
     * @throws RMIConfigurationException if a problem occurs in the configuration loading
     */
    public static void loadCarolConfiguration() throws RMIConfigurationException {
        // load the configuration files	
        try {

            defaultsProps = getDefaultsProperties();
            carolProps = getCarolProperties();
            jndiProps = getJndiProperties();

        } catch (Exception e) {
            TraceCarol.error("Exception occur when loading default/carol/jndi configuration file: ", e);
            throw new RMIConfigurationException("Exception occur when loading default/carol/jndi configuration file");
        }

        boolean cc = checkCarolConfiguration();
        // Check this properties and load the properties file 
        if (!cc)
            throw new RMIConfigurationException("Can't start Carol, configuration check fail");

        // translate existing jndi properties
        if (jndiProps != null) jndiProps = jndi2Carol(jndiProps);

        // build a general properties object
        Properties allProps = new Properties();

        // default properties can not be null (if null, checkCarolConfiguration should stop)
        allProps.putAll(defaultsProps);
        // first the jndi (extented) file 
        if (jndiProps != null) allProps.putAll(jndiProps);
        // second the carol file
        if (carolProps != null) allProps.putAll(carolProps);

        loadCarolConfiguration(allProps);

    }

    /**
     * This method read a carol configuration from a Properties object 
     * @throws RMIConfigurationException if a there is a problem with those environment (field missing for example)
     */
    public static synchronized void loadCarolConfiguration(Properties allProps) throws RMIConfigurationException {

        // prefix
        String jvmPref = CarolDefaultValues.CAROL_PREFIX + "." + CarolDefaultValues.JVM_PREFIX;
        String jndiPref = CarolDefaultValues.CAROL_PREFIX + "." + CarolDefaultValues.JNDI_PREFIX;

        // get the general properties
        // activated property : if existe use it, else use the jndi url property, else use the default property
        String act = allProps.getProperty(CarolDefaultValues.PROTOCOLS_KEY);
        if (act != null) {
            protocols = act.trim();
            allProps.remove(CarolDefaultValues.PROTOCOLS_KEY);
            if (TraceCarol.isDebugCarol()) {
                TraceCarol.debugCarol("Carol use carol file to activate RMI: " + protocols);
            }
        } else {
            //try the jndi rmi name 
            if (jndiRMIName != null) {
                protocols = jndiRMIName;
                if (TraceCarol.isDebugCarol()) {
                    TraceCarol.debugCarol("Carol use jndi file to activate RMI: " + protocols);
                }
            } else { //use the default
                protocols = allProps.getProperty(CarolDefaultValues.DEFAULT_PROTOCOLS_KEY).trim();
                if (TraceCarol.isDebugCarol()) {
                    TraceCarol.debugCarol("Carol use default file to activate RMI " + protocols);
                }
            }
        }

        startNS = new Boolean(allProps.getProperty(CarolDefaultValues.START_NS_KEY).trim()).booleanValue();
        startRMI = new Boolean(allProps.getProperty(CarolDefaultValues.START_RMI_KEY).trim()).booleanValue();
        startJNDI = new Boolean(allProps.getProperty(CarolDefaultValues.START_JNDI_KEY).trim()).booleanValue();

        // Trace Carol Global configuration
        if (TraceCarol.isDebugCarol()) {
            TraceCarol.debugCarol("--- Global Carol configuration: ---");
            TraceCarol.debugCarol("Multiple RMI is " + multiRMI);
            TraceCarol.debugCarol(CarolDefaultValues.START_NS_KEY + "=" + startNS);
            TraceCarol.debugCarol(CarolDefaultValues.START_RMI_KEY + "=" + startRMI);
            TraceCarol.debugCarol(CarolDefaultValues.START_JNDI_KEY + "=" + startJNDI);
        }

        //get all rmi name
        StringTokenizer pTok = new StringTokenizer(protocols, ",");
        if (pTok.countTokens() > 1) {
            multiRMI = true;
            // get all multi rmi function
            for (Enumeration e = allProps.propertyNames(); e.hasMoreElements();) {
                String pkey = ((String) e.nextElement()).trim();
                if (pkey.startsWith(CarolDefaultValues.MULTI_RMI_PREFIX)) {
                    allProps.setProperty(pkey.substring(CarolDefaultValues.MULTI_RMI_PREFIX.length() + 1),
					 (allProps.getProperty(pkey)).trim());
                    // set all multi rmi function
                    allProps.remove(pkey);
                }
            }

        } else {
            multiRMI = false;
            // remove all multi rmi function
            for (Enumeration e = allProps.propertyNames(); e.hasMoreElements();) {
                String pkey = ((String) e.nextElement()).trim();
                if (pkey.startsWith(CarolDefaultValues.MULTI_RMI_PREFIX)) {
                    // set all multi rmi function
                    allProps.remove(pkey);
                }
            }
        }

        // Trace Carol Global configuration
        if (TraceCarol.isDebugCarol()) {
            TraceCarol.debugCarol("--- Carol RMI configuration ---");
        }
        // load all RMI 
        defaultRMI = pTok.nextToken().trim();
        RMIConfiguration rmiConfDefault = new RMIConfiguration(defaultRMI, allProps);
        rmiConfigurationTable.put(defaultRMI, rmiConfDefault);

        // Trace Carol Default  configuration
        if (TraceCarol.isDebugCarol()) {
            TraceCarol.debugCarol("Carol RMI " + defaultRMI + " configuration:");
            TraceCarol.debugCarol(defaultRMI + " is default");
            // SortedMap of default rmi
            String rmiDP = CarolDefaultValues.CAROL_PREFIX + "." + defaultRMI;
            TreeMap map = new TreeMap(allProps);
            String k;
            for (Iterator e = map.keySet().iterator(); e.hasNext();) {
                k = (String) e.next();
                if (k.startsWith(rmiDP)) {
                    TraceCarol.debugCarol(k + "=" + allProps.getProperty(k));
                }
            }
        }

        String rmiName;
        while (pTok.hasMoreTokens()) {
            rmiName = pTok.nextToken().trim();
            RMIConfiguration rmiConf = new RMIConfiguration(rmiName, allProps);
            rmiConfigurationTable.put(rmiName, rmiConf);
            // Trace Carol Default  configuration
            if (TraceCarol.isDebugCarol()) {
                TraceCarol.debugCarol("Carol RMI " + rmiName + " configuration:");
                // SortedMap of default rmi
                String rmiDP = CarolDefaultValues.CAROL_PREFIX + "." + rmiName;
                TreeMap map = new TreeMap(allProps);
                String k;
                for (Iterator e = map.keySet().iterator(); e.hasNext();) {
                    k = (String) e.next();
                    if (k.startsWith(rmiDP)) {
                        TraceCarol.debugCarol(k + "=" + allProps.getProperty(k));
                    }
                }
            }
        }

        if (TraceCarol.isDebugCarol()) {
            TraceCarol.debugCarol("--- Carol JVM configuration --- (without " + jvmPref + " prefix)");
        }

        //Parse jvm the properties
        Properties jvmProps = new Properties();
        jvmProps.putAll(System.getProperties());

        // get all jvm configuration
        for (Enumeration e = allProps.propertyNames(); e.hasMoreElements();) {
            String pkey = ((String) e.nextElement()).trim();
            if (pkey.startsWith(jvmPref)) { // jvm properties
                jvmProps.setProperty(pkey.substring(jvmPref.length() + 1), (allProps.getProperty(pkey)).trim());
                if (TraceCarol.isDebugCarol()) {
                    TraceCarol.debugCarol(pkey.substring(jvmPref.length() + 1) + "=" + allProps.getProperty(pkey));
                }
            }
        }

        // get all jndi configuration (except rmi specific configuration)
        for (Enumeration e = allProps.propertyNames(); e.hasMoreElements();) {
            String pkey = ((String) e.nextElement()).trim();
            if (pkey.startsWith(jndiPref)) { // jndi properties
                jvmProps.setProperty(pkey.substring(jndiPref.length() + 1), (allProps.getProperty(pkey)).trim());
                if (TraceCarol.isDebugCarol()) {
                    TraceCarol.debugCarol(pkey.substring(jndiPref.length() + 1) + "=" + allProps.getProperty(pkey));
                }
            }
        }

        if (multiRMI) {
            // Set the system properties
            if (startRMI) {
                jvmProps.setProperty("javax.rmi.CORBA.PortableRemoteObjectClass", CarolDefaultValues.MULTI_PROD);
            }

            if (startJNDI) {
                jvmProps.setProperty("java.naming.factory.initial", CarolDefaultValues.MULTI_JNDI);
            }
        } else {
            // Set the system properties for only one protocol
            if (startRMI) {
                jvmProps.setProperty(
                    "javax.rmi.CORBA.PortableRemoteObjectClass",
                    ((RMIConfiguration) rmiConfigurationTable.get(defaultRMI)).getPro());
            }
            // Set the system properties for only one protocol
            if (startJNDI) {
                jvmProps.putAll(((RMIConfiguration) rmiConfigurationTable.get(defaultRMI)).getJndiProperties());
            }

        }

        // add the jvm properties in the jvm 
        System.setProperties(jvmProps);
        configurationLoaded = true;
        // start naming service
        if (startNS) {
            if (TraceCarol.isDebugCarol()) {
                TraceCarol.debugCarol("Start non started Name Servers");
            }
            try {
                NameServiceManager.startNonStartedNS();
            } catch (NameServiceException nse) {
                String msg = "Can't start Name Servers";
                TraceCarol.error(msg, nse);
                throw new RMIConfigurationException(msg);
            }
        }

    }

    /**
     * private static method mapping jndi properties to carol properties
     * @param jndi properties
     * @return carol jndi properties
     */
    private static Properties jndi2Carol(Properties p) {
        TraceCarol.debugCarol("map properties found in jndi.properties to CAROL ones");
        Properties result = new Properties();
        // get the rmi name 
        jndiRMIName = CarolDefaultValues.getRMIProtocol(p.getProperty(CarolDefaultValues.JNDI_URL_PREFIX));
        TraceCarol.debugCarol("rmi used=" + jndiRMIName);
        TraceCarol.debugCarol("initial properties = " + p);
        if (jndiRMIName == null) {
            return null;
        } else {
            for (Enumeration e = p.propertyNames(); e.hasMoreElements();) {
                String current = ((String) e.nextElement()).trim();
                if (current.trim().equals(CarolDefaultValues.JNDI_URL_PREFIX)) {
                    // URL prefix for my context
                    result.setProperty(CarolDefaultValues.CAROL_PREFIX + "." + 
				       jndiRMIName + "." + 
				       CarolDefaultValues.URL_PREFIX, p.getProperty(current));
                } else if (current.trim().equals(CarolDefaultValues.JNDI_FACTORY_PREFIX)) {
                    // CONTEXT FACTORY prefix for my 
                    result.setProperty(CarolDefaultValues.CAROL_PREFIX + "." + 
				       jndiRMIName + "." + 
				       CarolDefaultValues.FACTORY_PREFIX, p.getProperty(current));
		} else {
		    // Other jndi properties
                    result.setProperty(CarolDefaultValues.CAROL_PREFIX + "." + CarolDefaultValues.JNDI_PREFIX 
				       + "." + current, p.getProperty(current));
                }
            }
        }
        TraceCarol.debugCarol("resulting properties = " + result);
        return result;
    }

    /**
     * load a properties file from a classloader
     * @param String properties file name (without '.properties')
     * @param Classloader
     * @return Properties file (null if there is no prperties)
     */
    private static Properties loadPropertiesFile(String fName, ClassLoader cl) throws Exception {
        Properties result = null;
        // load the defaults configuration file
        InputStream fInputStream = cl.getResourceAsStream(fName + ".properties");
        if (fInputStream == null) {
            // resource not found direcly, search in the jars
            ResourceBundle rb = ResourceBundle.getBundle(fName, Locale.getDefault(), cl);
            if (rb.getKeys().hasMoreElements()) {
                String key;
                result = new Properties();
                for (Enumeration e = rb.getKeys(); e.hasMoreElements();) {
                    key = (String) e.nextElement();
                    result.setProperty(key, rb.getString(key));
                }
                if (TraceCarol.isDebugCarol()) {
                    TraceCarol.debugCarol("Carol file used is " + fName + ".properties through URLClassLoader");
                }
            }
        } else {
            result = new Properties();
            result.load(fInputStream);
            if (TraceCarol.isDebugCarol()) {
                TraceCarol.debugCarol(
                    "Carol file used is "
                        + fName
                        + ".properties in "
                        + cl.getResource(fName + ".properties").getPath());
            }
        }
        if (result == null) {
            if (TraceCarol.isDebugCarol()) {
                TraceCarol.debugCarol("No " + fName + ".properties file found");
            }
        }
        return result;
    }

    /**
     * find a properties file from a classloader
     * @param String properties file name (without '.properties')
     * @param Classloader
     * @return String the location of this properties 
     */
    private static String findPropertiesFile(String fName, ClassLoader cl) throws Exception {
        String result = "";
        // load the defaults configuration file
        InputStream fInputStream = cl.getResourceAsStream(fName + ".properties");
        if (fInputStream == null) {
            // resource not found direcly, search through URLClassLoader
            ResourceBundle rb = ResourceBundle.getBundle(fName, Locale.getDefault(), cl);
            if (rb.getKeys().hasMoreElements()) {
                result = "Carol file used is " + fName + ".properties through URLClassLoader";
            }
        } else {
            result =
                "Carol file used is "
                    + fName
                    + ".properties in "
                    + cl.getResource(fName + ".properties").getPath();
        }
        if (result == null) {
            if (TraceCarol.isDebugCarol()) {
                TraceCarol.debugCarol("No " + fName + ".properties file found");
            }
        }
        return result;
    }

    /**
     * get defaults properties from file
     * @return Properties default properties
     */
    private static Properties getDefaultsProperties() throws Exception {
        return loadPropertiesFile("carol-defaults", Thread.currentThread().getContextClassLoader());
    }

    /**
     * get carol properties from file
     * @return Properties carol properties
    */
    private static Properties getCarolProperties() throws Exception {
        Properties props = null;
        try {
            props = loadPropertiesFile("carol", Thread.currentThread().getContextClassLoader());
        } catch (Exception e) {
            TraceCarol.debugCarol("carol.properties file not found: " + e);
        }
        return props;
    }

    /**
     * get jndi properties from file
     * @return Properties default properties
    */
    private static Properties getJndiProperties() {
        Properties props = null;
        try {
            props = loadPropertiesFile("jndi", Thread.currentThread().getContextClassLoader());
        } catch (Exception e) {
            TraceCarol.debugCarol("jndi.properties file not found: " + e);
        }
        return props;
    }

    /**
     * public static boolean check communication configuration method
     * @param carol properties
     * @return boolean true if the configuration seam to be ok
     */
    public static boolean checkCarolConfiguration() {
        boolean result = true;

        //check if there is a default properties 
        if (defaultsProps == null)
            result = false;

        //this is a carol check with 
        return true;
    }

    /**
     * public static boolean check communication configuration method
     * @return boolean true if the configuration seam to be ok
     */
    public static String getCarolConfiguration() {
        String result = "";
        Properties dProps = null;
        Properties cProps = null;
        Properties jProps = null;

        try {
            result = loadPropertiesFile("carol-defaults", Thread.currentThread().getContextClassLoader()) + "\n";
            result = loadPropertiesFile("carol", Thread.currentThread().getContextClassLoader()) + "\n";
            result = loadPropertiesFile("jndi", Thread.currentThread().getContextClassLoader()) + "\n";
        } catch (Exception e) {
            result += "There is a problem with the configuration loading:" + e;
        }

        //check if there is a default properties 
        if (defaultsProps == null)
            result += "Default carol configuration file missing\n";
        // build a general properties object
        Properties allProps = new Properties();

        // default properties can not be null (if null, checkCarolConfiguration should stop)
        if (defaultsProps != null)
            allProps.putAll(defaultsProps);
        // first the jndi (extented) file 
        if (jndiProps != null)
            allProps.putAll(jndiProps);
        // second the carol file
        if (carolProps != null)
            allProps.putAll(carolProps);
        result += "Global Carol configuration is:";
        // get all carol configuration
        // SortedMap of allPorps
        TreeMap map = new TreeMap(allProps);
        String k;
        for (Iterator e = map.keySet().iterator(); e.hasNext();) {
            k = (String) e.next();
            result += k + "=" + allProps.getProperty(k);
        }
        return result;
    }

    /**
     * public static String, get activated carol protocols
     * @return String activated protocols
     */
    public static String getProtocols() {
	return protocols;
    }

    /**
     * Add interceptors facility for protocols
     * @param String protocol name
     * @param String Interceptor Intializer class name  
     */
    public static void addInterceptors(String protocolName, String interceptorInitializer) throws RMIConfigurationException {
	RMIConfiguration rc = getRMIConfiguration(protocolName);
	if (rc!=null) {
	    String pref=rc.getInterceptorPrefix();
	    if (pref!=null) {
		System.setProperty(pref+"."+interceptorInitializer,"");
		if (TraceCarol.isDebugCarol()) {
		    TraceCarol.debugCarol("Add Initializer for " +  protocolName + ": " +pref+"."+interceptorInitializer);
		}
	    }
	}
    }
     

}