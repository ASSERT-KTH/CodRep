// using default english language, shipped with Columba

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

package org.columba.core.util;

import org.columba.core.main.MainInterface;
import org.columba.core.xml.XmlElement;

import java.io.File;
import java.io.FileFilter;

import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;

import java.util.Enumeration;
import java.util.HashSet;
import java.util.Hashtable;
import java.util.Locale;
import java.util.MissingResourceException;
import java.util.ResourceBundle;
import java.util.Set;
import java.util.StringTokenizer;
import java.util.logging.Logger;


/*
        Comments: this is the core class to handle i18n in columba, loading, handling and returning localized strings.
        It should not be used directly, use MailResourceLoader or AddressbookResourceLoader (or *ResourceLoader) instead.

        Behaviour:
        When a resource is needed, getString() or getMnemonics() are called. They look for a resource with that name (in the current locale bundles).
        If it is not found, they look for the resource in the global resource bundle (for the current locale). If this is not found, "FIXME" is returned.

        Example of usage: We need to get the text for "my_cool_button" located into "org/columba/modules/mail/i18n/action/something_else_than_action"
        sPath: org/columba/modules/mail/i18n/action/ => The complete package path.
        sName: something_else_than_action => the name of the _it_IT.properties file.
        sID: my_cool_button => the name to be looked for inside sName file.
        We can call:
        a) MailResourceLoader.getString("action", "something_else_than_action", "my_cool_button");
        b) ResourceLoader.getString("org/columba/modules/mail/i18n/action", "something_else_than_action", "my_cool_button");
        They'll both work.

        We need to gets its mnemonic:
        a) MailResourceLoader.getMnemonic("action", "something_else_than_action", "my_cool_button");
        b) ResourceLoader.getMnemonic("org/columba/modules/mail/i18n/action", "something_else_than_action", "my_cool_button");
*/
public class GlobalResourceLoader {

    private static final Logger LOG = Logger.getLogger("org.columba.core.util");

    protected static ClassLoader classLoader;
    protected static Hashtable htBundles = new Hashtable(80);
    protected static ResourceBundle globalBundle;
    private static final String GLOBAL_BUNDLE_PATH = "org.columba.core.i18n.global.global";

    static {
        //use english as default
        XmlElement locale = new XmlElement("locale");
        locale.addAttribute("language", "en");

        String language = locale.getAttribute("language");
        String country = locale.getAttribute("country", "");
        String variant = locale.getAttribute("variant", "");
        Locale.setDefault(new Locale(language, country, variant));
    }

    /**
     * Initialize in org.columba.core.main.Main to use user-definable
     * language pack.
     */
    public static void loadLanguage() {
        XmlElement locale = MainInterface.config.get("options").getElement("/options/locale");

        // no configuration available, create default config
        if (locale == null) {
            // create new locale xml treenode
            locale = new XmlElement("locale");
            locale.addAttribute("language", "en");
            MainInterface.config.get("options").getElement("/options").addElement(locale);
        }

        String language = locale.getAttribute("language");
        String country = locale.getAttribute("country", "");
        String variant = locale.getAttribute("variant", "");
        Locale.setDefault(new Locale(language, country, variant));
        initClassLoader();

        try {
            // use ResourceBundle's internal classloader
            if (classLoader == null) {
                globalBundle = ResourceBundle.getBundle(GLOBAL_BUNDLE_PATH,
                        Locale.getDefault());
            } else {
                globalBundle = ResourceBundle.getBundle(GLOBAL_BUNDLE_PATH,
                        Locale.getDefault(), classLoader);
            }
        } catch (MissingResourceException mre) {
            throw new RuntimeException(
                "Global resource bundle not found, Columba cannot start.");
        }
    }

    public static Locale[] getAvailableLocales() {
        Set locales = new HashSet();
        locales.add(new Locale("en", ""));

        FileFilter langpackFileFilter = new LangPackFileFilter();
        File[] langpacks = MainInterface.config.getConfigDirectory().listFiles(langpackFileFilter);

        for (int i = 0; i < langpacks.length; i++) {
            locales.add(extractLocaleFromFilename(langpacks[i].getName()));
        }

        langpacks = new File(".").listFiles(langpackFileFilter);

        for (int i = 0; i < langpacks.length; i++) {
            locales.add(extractLocaleFromFilename(langpacks[i].getName()));
        }

        return (Locale[]) locales.toArray(new Locale[0]);
    }

    private static Locale extractLocaleFromFilename(String name) {
        String language = "";
        String country = "";
        String variant = "";
        name = name.substring(9, name.length() - 4);

        StringTokenizer tokenizer = new StringTokenizer(name, "_");

        if (tokenizer.hasMoreElements()) {
            language = tokenizer.nextToken();

            if (tokenizer.hasMoreElements()) {
                country = tokenizer.nextToken();

                if (tokenizer.hasMoreElements()) {
                    variant = tokenizer.nextToken();
                }
            }
        }

        return new Locale(language, country, variant);
    }

    protected static void initClassLoader() {
        String name = "langpack_" + Locale.getDefault().toString() + ".jar";
        File langpack = new File(MainInterface.config.getConfigDirectory(), name);

        if (!langpack.exists() || !langpack.isFile()) {
            langpack = new File(".", name);
        }

        if (langpack.exists() && langpack.isFile()) {
            LOG.fine("Creating new i18n class loader for " + langpack.getPath());

            try {
                classLoader = new URLClassLoader(new URL[] {langpack.toURL()});
            } catch (MalformedURLException mue) {
            }
             //does not occur
        } else {
            LOG.severe("No language pack found for " + Locale.getDefault().toString());

            // we can't use SystemClassLoader here, because that
            // wouldn't work with java webstart,
            // ResourceBundle uses its own internal classloader
            // if no classloader is given
            //  -> set classloader = null
            /*
            classLoader = ClassLoader.getSystemClassLoader();
            */
            classLoader = null;
        }
    }

    protected static String generateBundlePath(String sPath, String sName) {
        return sPath + "." + sName;
    }

    /*
            This method returns the translation for the given string identifier. If no translation is found, the default english item is used.
            Should this fail too, the sID string will be returned.

            Example usage call: getString("org/columba/modules/mail/i18n/", "dialog", "close")
            We'll look for "close" in "org/columba/modules/mail/i18n/dialog/dialog_locale_LOCALE.properties"
            Thus:
            sPath: "org/columba/modules/mail/i18n/dialog"
            sName: "dialog"
            sID: "close"
            The bundle name will be: "org/columba/modules/mail/i18n/dialog/dialog"

            Hypotetically this method should not be available to classes different from *ResourceLoader
            (example: MailResourceLoader, AddressbookResourceLoader); this means that *ResourceLoader classes *do know* how to call this method.
    */
    public static String getString(String sPath, String sName, String sID) {
        if ((sID == null) || sID.equals("")) {
            return null;
        }

        ResourceBundle bundle = null;
        String sBundlePath = null;

        if ((sPath != null) && !sPath.equals("")) {
            //Find out if we already loaded the needed ResourceBundle
            //object in the hashtable.
            sBundlePath = generateBundlePath(sPath, sName);
            bundle = (ResourceBundle) htBundles.get(sBundlePath);
        }

        if ((bundle == null) && (sBundlePath != null)) {
            try {
                // use ResourceBundle's internal classloader
                if (classLoader == null) {
                    bundle = ResourceBundle.getBundle(sBundlePath,
                            Locale.getDefault());
                } else {
                    bundle = ResourceBundle.getBundle(sBundlePath,
                            Locale.getDefault(), classLoader);
                }

                htBundles.put(sBundlePath, bundle);
            } catch (MissingResourceException mre) {
            }
        }

        if (bundle != null) {
            try {
                return bundle.getString(sID);
            } catch (MissingResourceException mre) {
            }
        }

        try {
            return globalBundle.getString(sID);
        } catch (MissingResourceException mre) {
            LOG.severe("'" + sID + "' in '" + sBundlePath + "' could not be found.");

            return sID;
        }
    }

    public static void reload() {
        initClassLoader();
        LOG.fine("Reloading cached resource bundles for locale " + Locale.getDefault().toString());

        try {
            // use ResourceBundle's internal classloader
            if (classLoader == null) {
                globalBundle = ResourceBundle.getBundle(GLOBAL_BUNDLE_PATH,
                        Locale.getDefault());
            } else {
                globalBundle = ResourceBundle.getBundle(GLOBAL_BUNDLE_PATH,
                        Locale.getDefault(), classLoader);
            }
        } catch (MissingResourceException mre) {
        }
         //should not occur, otherwise the static initializer should have thrown a RuntimeException

        String bundlePath;
        ResourceBundle bundle;

        for (Enumeration entries = htBundles.keys(); entries.hasMoreElements();) {
            try {
                bundlePath = (String) entries.nextElement();

                //retrieve new bundle
                // use ResourceBundle's internal classloader
                if (classLoader == null) {
                    bundle = ResourceBundle.getBundle(bundlePath,
                            Locale.getDefault());
                } else {
                    bundle = ResourceBundle.getBundle(bundlePath,
                            Locale.getDefault(), classLoader);
                }

                //overwrite old bundle
                htBundles.put(bundlePath, bundle);
            } catch (MissingResourceException mre) {
            }
             //should not occur, otherwise the bundlePath would not be in the hashtable
        }
    }

    public static class LangPackFileFilter implements FileFilter {
        public boolean accept(File file) {
            String name = file.getName().toLowerCase();

            return file.isFile() && name.startsWith("langpack_")
                && name.endsWith(".jar");
        }
    }
}