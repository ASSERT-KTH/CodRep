private static Locale LAST_RESORT = new Locale("en","");

package org.tigris.scarab.tools;

/* ================================================================
 * Copyright (c) 2000 CollabNet.  All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 * 
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 * 
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 * 
 * 3. The end-user documentation included with the redistribution, if
 * any, must include the following acknowlegement: "This product includes
 * software developed by CollabNet (http://www.collab.net/)."
 * Alternately, this acknowlegement may appear in the software itself, if
 * and wherever such third-party acknowlegements normally appear.
 * 
 * 4. The hosted project names must not be used to endorse or promote
 * products derived from this software without prior written
 * permission. For written permission, please contact info@collab.net.
 * 
 * 5. Products derived from this software may not use the "Tigris" name
 * nor may "Tigris" appear in their names without prior written
 * permission of CollabNet.
 * 
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL COLLAB.NET OR ITS CONTRIBUTORS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
 * IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 * ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * ====================================================================
 * 
 * This software consists of voluntary contributions made by many
 * individuals on behalf of CollabNet.
 */

import java.util.ArrayList;
import java.util.Collection;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.MissingResourceException;
import java.util.ResourceBundle;
import javax.servlet.http.HttpServletRequest;
import org.apache.commons.configuration.Configuration;
import org.apache.fulcrum.localization.LocaleTokenizer;
import org.apache.fulcrum.localization.Localization;
import org.apache.fulcrum.localization.LocalizationService;
import org.apache.turbine.RunData;
import org.apache.turbine.Turbine;
import org.apache.turbine.tool.LocalizationTool;
import org.tigris.scarab.util.Log;
import org.tigris.scarab.util.ReferenceInsertionFilter;
import org.tigris.scarab.util.SkipFiltering;

/**
 * Scarab-specific localiztion tool.  Uses the following property
 * format to access Turbine's properties (generally defined in
 * <code>Scarab.properties</code>):
 * 
 * <blockquote><code><pre>
 *  template.[dir/]&lt;scope&gt;.&lt;title&gt;
 * </pre></code> </blockquote>
 * 
 * Defaults for scope can be specified using the
 * <code>default.somevar</code> syntax, where <code>somevar</code> is
 * the variable you want to specify a default scope for.
 * 
 * @author <a href="mailto:dlr@collab.net">Daniel Rall </a>
 */
public class ScarabLocalizationTool extends LocalizationTool
{
    /**
     * The Locale to be used, if the Resource could not be found in
     * one of the Locales specified in the Browser's language preferences.
     */
    private static Locale LAST_RESORT = new Locale("en");

    /**
     * The portion of a key denoting the default scope 
     * (the default target name).
     */
    private static final String DEFAULT_SCOPE = "default";

    /**
     * The portion of a key denoting the title property.
     */
    private static final String TITLE_PROP = "title";

    /**
     * We need to keep a reference to the request's <code>RunData</code> so
     * that we can extract the name of the target <i>after </i> the <code>Action</code>
     * has run (which may have changed the target from its original value as a
     * sort of internal redirect).
     */
    private RunData data;

    /**
     * Initialized by <code>init()</code>, 
     * cleared by <code>refresh()</code>.
     */
    private Configuration properties;
    private String bundlePrefix;
    private String oldBundlePrefix;

    /**
     * Store the collection of locales to be used for ResourceBundle resolution.
     * If the Class is instantiated from RunData, the collection contains all
     * Locales in order of preference as specified in the Browser.
     * If the Class is instantiated from a Locale, the collection contains
     * just that Locale.
     * 
     */
    private Collection locales;

    /**
     * true: enables cross-site scripting filtering.
     * @see resolveArgumentTemplates 
     * @see format(String, Object[])
     */
    private boolean filterEnabled = true;

    /**
     * Creates a new instance.  Client should 
     * {@link #init(Object) initialize} the instance.
     */
    public ScarabLocalizationTool()
    {
    }

    /**
     * Return the localized property value.
     * Take into account the Browser settings (in order of preference), 
     * the Turbine default settings and the System Locale, 
     * if the Turbine Default Locale is not defined.
     */
    public String get(String key)
    {
        String value = null;
        try
        {
            // Try with all defined "Browser"-Locales ordered by relevance
            Iterator iter = locales.iterator();
            while (value == null && iter.hasNext())
            {
                Locale locale = (Locale) iter.next();
                value = resolveKey(key, locale);
            }
            if (value == null)
            {
                // Try to resolve from the LAST_RESORT Locale (en)
                value = resolveKey(key, LAST_RESORT);
                if (value == null)
                {
                    //Try with the "Default"-Locale
                    value = resolveKey(key, null);
                    if (value == null)
                    {
                        //Try to find default.<key> ??? (This seems to be wrong ...[Hussayn])
                        value = super.get(DEFAULT_SCOPE + '.', key);
                        if (value == null)
                        {
                            // give up
                            value = createMissingResourceValue(key);
                        }
                    }
                }
            }
        }
        catch (Exception e)
        {
            value = createBadResourceValue(key, e);
        }
        return value;
    }

    /**
     * Formats a localized value using the provided object.
     * 
     * @param key  The identifier for the localized text to retrieve,
     * @param arg1 The object to use as {0} when formatting the localized text.
     * @return     Formatted localized text.
     * @see        #format(String, List)
     */
    public String format(String key, Object arg1)
    {
        return format(key, new Object[]{arg1});
    }

    /**
     * Formats a localized value using the provided objects.
     * 
     * @param key  The identifier for the localized text to retrieve,
     * @param arg1 The object to use as {0} when formatting the localized text.
     * @param arg2 The object to use as {1} when formatting the localized text.
     * @return     Formatted localized text.
     * @see        #format(String, List)
     */
    public String format(String key, Object arg1, Object arg2)
    {
        return format(key, new Object[]{arg1, arg2});
    }

    /**
     * Formats a localized value using the provided objects.
     * 
     * @param key  The identifier for the localized text to retrieve,
     * @param arg1 The object to use as {0} when formatting the localized text.
     * @param arg2 The object to use as {1} when formatting the localized text.
     * @param arg3 The object to use as {2} when formatting the localized text.
     * @return     Formatted localized text.
     * @see        #format(String, List)
     */
    public String format(String key, Object arg1, Object arg2, Object arg3)
    {
        return format(key, new Object[]{arg1, arg2, arg3});
    }

    /**
     * <p>Formats a localized value using the provided objects.</p>
     * 
     * <p>ResourceBundle:
     * <blockquote><code><pre>
     *  VelocityUsersNotWrong={0} out of {1} users can't be wrong!
     * </pre></code> </blockquote>
     * 
     * Template:
     * <blockquote><code><pre>
     * $l10n.format("VelocityUsersNotWrong", ["9", "10"])
     * </pre></code> </blockquote>
     * 
     * Result:
     * <blockquote><code><pre>
     *  9 out of 10 Velocity users can't be wrong!
     * </pre></code></blockquote></p>
     * 
     * @param key  The identifier for the localized text to retrieve,
     * @param args The objects to use as {0}, {1}, etc. when formatting the
     *             localized text.
     * @return     Formatted localized text.
     */
    public String format(String key, List args)
    {
        Object[] array = (args==null) ? null: args.toArray();
        return format(key, array);
    }

    /**
     * Allow us to be able to enable/disable our cross-site scripting filter
     * when rendering something from the format() method. The default is to
     * have it enabled.
     */
    public void setFilterEnabled(boolean v)
    {
        filterEnabled = v;
    }

    /**
     * Whether our cross-site scripting filter is enabled.
     */
    public boolean isFilterEnabled()
    {
        return filterEnabled;
    }

    /**
     * Formats a localized value using the provided objects.
     * Take into account the Browser settings (in order of preference), 
     * the Turbine default settings and the System Locale, 
     * if the Turbine Default Locale is not defined.
     * 
     * @param key  The identifier for the localized text to retrieve,
     * @param args The <code>MessageFormat</code> data used when formatting
     *             the localized text.
     * @return     Formatted localized text.
     * @see        #format(String, List)
     */
    public String format(String key, Object[] args)
    {
        String value = null;
        resolveArgumentTemplates(args);
        try
        {
            // try with the "Browser"-Locale
            Iterator iter = locales.iterator();
            while (value == null && iter.hasNext())
            {
                Locale locale = (Locale) iter.next();
                value = formatKey(key, args, locale);
            }
            if (value == null)
            {
                // Try to resolve from the LAST_RESORT Locale (en)
                value = formatKey(key, args, LAST_RESORT);
                if (value == null)
                {
                    // try with the "Default"-Locale
                    value = formatKey(key, args, null);
                    if (value == null)
                    {
                        // try with the "Default"-Scope ??? This may be wrong (Hussayn)
                        String prefix = getPrefix(null);
                        setPrefix(DEFAULT_SCOPE + '.');
                        try
                        {
                            value = super.format(key, args);
                        }
                        catch (MissingResourceException itsNotThere)
                        {
                            value = createMissingResourceValue(key);
                        }
                        setPrefix(prefix);
                    }
                }
            }
        }
        catch (Exception e)
        {
            value = createBadResourceValue(key, e);
        }
        return value;
    }



    /**
     * Provides <code>$l10n.Title</code> to templates, grabbing it
     * from the <code>title</code> property for the current template.
     * 
     * @return The title for the template used in the current request, or
     *         <code>null</code> if title property was not found in
     *         the available resource bundles.
     */
    public String getTitle()
    {
        String title = findProperty(TITLE_PROP, false);
        if (title == null)
        {
            // Either the property name doesn't correspond to a
            // localization key, or the localization property pointed
            // to by the key doesn't have a value. Try the default.
            title = findProperty(TITLE_PROP, true);

            // If no default localization this category of template
            // property was available, we return null so the VTL
            // renders literally and the problem can be detected.
        }
        return title;
    }

    /**
     * Retrieves the localized version of the value of <code>property</code>.
     * 
     * @param property 
     *        The name of the property whose value to retrieve.
     * @param useDefaultScope
     *        Whether or not to use the default scope (defined by the
     *        <code>DEFAULT_SCOPE</code> constant).
     * @return The localized property value.
     */
    protected String findProperty(String property, boolean useDefaultScope)
    {
        String value = null;
        if (properties != null)
        {
            String templateName = (useDefaultScope || data == null) ? 
            DEFAULT_SCOPE : data.getTarget().replace(',', '/');
            String propName = "template." + templateName + '.' + property;
            String l10nKey = properties.getString(propName);
            Log.get().debug(
            "ScarabLocalizationTool: Property name '" + propName + 
            "' -> localization key '" + l10nKey + '\'');
            if (l10nKey != null)
            {
                String prefix = getPrefix(templateName + '.');
                if (prefix != null)
                {
                    l10nKey = prefix + l10nKey;
                }
                value = get(l10nKey);
                Log.get().debug("ScarabLocalizationTool: Localized value is '" + 
                value + '\'');
            }
        }
        return value;
    }

    /**
     * Change the BundlePrefix. Keep the original value for later
     * restore
     * @param prefix
     */
    public void setBundlePrefix(String prefix)
    {
        oldBundlePrefix = bundlePrefix;
        bundlePrefix = prefix;
    }

    /**
     * Restore the old Bundle Prefix to it's previous value.
     */
    public void restoreBundlePrefix()
    {
        bundlePrefix = oldBundlePrefix;
    }


    /**
     * Get the default ResourceBundle name
     */
    protected String getBundleName()
    {
        String name = Localization.getDefaultBundleName();
        return (bundlePrefix == null) ? name : bundlePrefix + name;
    }

    /**
     * @deprecated. Gets the current locale.
     * This method is obsolete 
     * and should be completely removed from this class.
     * Not sure about the implications though.[HD]
     * @return The locale currently in use.
     */
    public Locale getLocale()
    {
        return (locales == null || locales.size()==0) 
        ?  super.getLocale()
        : (Locale) locales.iterator().next();
    }

    // ---- ApplicationTool implementation ----------------------------------

    /**
     * Initialize the tool. Within the turbine pull service this tool is
     * initialized with a RunData. However, the tool can also be initialized
     * with a Locale.
     */
    public void init(Object obj)
    {
        super.init(obj);
        if (obj instanceof RunData)
        {
            data = (RunData) obj;
            locales = getBrowserLocales();
        }
        else if (obj instanceof Locale)
        {
            locales = new ArrayList();
            locales.add(obj);
        }
        properties = Turbine.getConfiguration();
    }

    /**
     * Reset this instance to initial values.
     * Probably needed for reuse of ScarabLocalizationTool Instances.
     */
    public void refresh()
    {
        super.refresh();
        data = null;
        properties = null;
        bundlePrefix = null;
        oldBundlePrefix = null;
        locales = null;
        setFilterEnabled(true);
    }


    // ===========================
    // Private utility methods ...
    // ===========================

    /**
     * Utility method: Get a Collection of possible locales 
     * to be used as specified in the Browser settings.
     * @return
     */
    private Collection getBrowserLocales()
    {
        Collection result = new ArrayList(3);
        String localeAsString = getBrowserLocalesAsString();
        LocaleTokenizer localeTokenizer = new LocaleTokenizer(localeAsString);
        while (localeTokenizer.hasNext())
        {
            Locale browserLocale = (Locale) localeTokenizer.next();
            Locale finalLocale = getFinalLocaleFor(browserLocale);
            if (finalLocale != null)
            {
                result.add(finalLocale);
            }
        }
        return result;
    }


    /**
     * Contains a map of Locales which support given
     * browserLocales.
     */
    static private Map supportedLocaleMap = new Hashtable();
    /**
     * Contains a map of Locales which do NOT support given
     * browserLocales.
     */
    static private Map unsupportedLocaleMap = new Hashtable();

    /**
     * Return the locale, which will be used to resolve
     * keys of the given browserLocale. This method returns
     * null, when Scarab does not directly support the 
     * browserLocale. Which means: The browser Locale leads
     * to a Resource Bundle of another language.
     * @param browserLocale
     * @return 
     */
    private Locale getFinalLocaleFor(Locale browserLocale)
    {
        Locale result = (Locale) supportedLocaleMap.get(browserLocale);
        if (result == null)
        {
            if (unsupportedLocaleMap.get(browserLocale) == null)
            {
                ResourceBundle bundle = ResourceBundle.getBundle(
                        getBundleName(), 
                        browserLocale);
                if (bundle != null)
                {
                    Locale finalLocale = bundle.getLocale();
                    String initialLanguage = browserLocale.getLanguage();
                    String finalLanguage = finalLocale.getLanguage();
                    if (initialLanguage.equals(finalLanguage))
                    {
                        result = finalLocale;
                        supportedLocaleMap.put(browserLocale, finalLocale);
                    }
                    else
                    {
                        unsupportedLocaleMap.put(browserLocale, finalLocale);
                    }
                }
                else
                {
                    Log.get().error(
                    "ScarabLocalizationTool: ResourceBundle '"
                    + getBundleName() + 
                    "' -> not resolved for Locale '"
                    + browserLocale
                    + "'. This should never happen.");
                }
            }
        }
        return result;
    }

    /**
     * Utility method: Get the content of the Browser localizationj settings.
     * Return an empty String when no Browser settings are defined.
     * @param acceptLanguage
     * @param request
     */
    private String getBrowserLocalesAsString()
    {
        String acceptLanguage = LocalizationService.ACCEPT_LANGUAGE;
        HttpServletRequest request = data.getRequest();
        String browserLocaleAsString = request.getHeader(acceptLanguage);
        if (browserLocaleAsString == null)
        {
            browserLocaleAsString = "";
        }
        return browserLocaleAsString;
    }

    /**
     * Utility method: Resolve a given key using the given Locale.
     * If the key can not be resolved, return null
     * @param key
     * @param locale
     * @return
     */
    private String resolveKey(String key, Locale locale)
    {
        String value;
        try
        {
            value = Localization
            .getString(getBundleName(), locale, key);
        }
        catch (MissingResourceException noKey)
        {
            // No need for logging (already done in base class).
            value = null;
        }
        return value;
    }


    /**
     * Utility method: Resolve a given key using the given Locale and apply 
     * the resource formatter. If the key can not be resolved, 
     * return null
     * @param key
     * @param args
     * @param locale
     * @return
     */
    private String formatKey(String key, Object[] args, Locale locale)
    {
        String value;
        try
        {
            value = Localization.format(getBundleName(), locale, key, 
            args);
        }
        catch (MissingResourceException noKey)
        {
            value = null;
        }
        return value;
    }

    /**
     * Utility method: Resolve $variables placed within the args.
     * Used before actually calling the resourceBundle formatter.
     * @param args
     * @return a cloned args list, or args when
     *         filtering is disabled. If args is null, also
     *         return null.
     */
    private Object[] resolveArgumentTemplates(Object[] args)
    {
        // we are going to allow html text within resource bundles. This
        // avoids problems in translations when links or other html tags
        // would result in an unnatural breakup of the text. We need
        // to apply the filtering here on the arguments which might contain
        // user entered data, if we are going to skip the filtering later.

        Object[] result;
        if (isFilterEnabled() && args != null && args.length > 0)
        {
            result = new Object[args.length];
            for (int i = 0; i < args.length; i++)
            {
                Object obj = args[i];
                // we don't filter Number, because these are sometimes passed
                // to message formatter in order to make a choice. Converting
                // the number to a String will cause error
                if (obj != null)
                {
                 if(! (     (obj instanceof SkipFiltering)
                         || (obj instanceof Number))
                 )
                 {
                    obj = ReferenceInsertionFilter.filter(obj.toString());
                 }
                }
                result[i] = obj;
            }
        }
        else
        {
            result = args;
        }
        return result;
    }

    /**
     * Utility method: create a Pseudovalue when the key
     * has no resolution at all.
     * @param key
     * @return
     */
    private String createMissingResourceValue(String key)
    {
        String value;
        value = "ERROR! Missing resource (" + key + ")("
        + Locale.getDefault() + ")";
        Log.get().error(
        "ScarabLocalizationTool: ERROR! Missing resource: "
        + key);
        return value;
    }

    /**
     * Utility method: create a Pseudovalue when the key
     * can not be used as resource key.
     * @param key
     * @param e
     * @return
     */
    private String createBadResourceValue(String key, Exception e)
    {
        String value;
        value = "ERROR! Bad resource (" + key + ")";
        Log.get().error(
        "ScarabLocalizationTool: ERROR! Bad resource: " + key
        + ".  See log for details.", e);
        return value;
    }
}