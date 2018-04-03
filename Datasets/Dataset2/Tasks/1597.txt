value = super.get(key);

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

import java.util.List;
import java.util.MissingResourceException;

import org.apache.commons.configuration.Configuration;
import org.apache.fulcrum.localization.Localization;
import org.apache.turbine.RunData;
import org.apache.turbine.Turbine;
import org.apache.turbine.tool.LocalizationTool;
import org.tigris.scarab.util.Log;
import org.tigris.scarab.util.ReferenceInsertionFilter;
import org.tigris.scarab.util.ScarabLink;
import org.tigris.scarab.util.SkipFiltering;

/**
 * Scarab-specific localiztion tool.  Uses the following property
 * format to access Turbine's properties (generally defined in
 * <code>Scarab.properties</code>):
 *
 * <blockquote><code><pre>
 * template.[dir/]&lt;scope&gt;.&lt;title&gt;
 * </pre></code></blockquote>
 *
 * Defaults for scope can be specified using the
 * <code>default.somevar</code> syntax, where <code>somevar</code> is
 * the variable you want to specify a default scope for.
 *
 * @author <a href="mailto:dlr@collab.net">Daniel Rall</a>
 */
public class ScarabLocalizationTool
    extends LocalizationTool
{
    /**
     * The portion of a key denoting the default scope (the default
     * target name, for instance).
     */
    private static final String DEFAULT_SCOPE = "default";

    /**
     * The portion of a key denoting the 
     */
    private static final String TITLE_PROP = "title";

    /**
     * We need to keep a reference to the request's
     * <code>RunData</code> so that we can extract the name of the
     * target <i>after</i> the <code>Action</code> has run (which may
     * have changed the target from its original value as a sort of
     * internal redirect).
     */
    private RunData data;

    /**
     * Initialized by <code>init()</code>, cleared by
     * <code>refresh()</code>.
     */
    private Configuration properties;

    private String bundlePrefix;
    private String oldBundlePrefix;

    /**
     * Creates a new instance.
     */
    public ScarabLocalizationTool()
    {
        super();
    }

    public String get(String key)
    {
        String value = null;
        try 
        {
            super.get(key);
            if (value == null)
            {
                value = super.get(DEFAULT_SCOPE + '.', key);
            }
            if (value == null) 
            {
                value = "ERROR! Missing resource (" + key + ")";
                Log.get().error(
                    "ScarabLocalizationTool: ERROR! Missing resource: " + key);
            }
        }
        catch (Exception e)
        {
            value = "ERROR! Bad resource (" + key + ")";
            Log.get().error(
                "ScarabLocalizationTool: ERROR! Bad resource: " + key + 
                ".  See log for details.", e);
        }

        return value;
    }


   /**
     * Formats a localized value using the provided object.
     *
     * @param key The identifier for the localized text to retrieve,
     * @param arg1 The object to use as {0} when formatting the localized text.
     * @return Formatted localized text.
     * @see #format(String, List)
     */
    public String format(String key, Object arg1)
    {
        return format(key, new Object[] {arg1});
    }

    /**
     * Formats a localized value using the provided objects.
     *
     * @param key The identifier for the localized text to retrieve,
     * @param arg1 The object to use as {0} when formatting the localized text.
     * @param arg2 The object to use as {1} when formatting the localized text.
     * @return Formatted localized text.
     * @see #format(String, List)
     */
    public String format(String key, Object arg1, Object arg2)
    {
        return format(key, new Object[] {arg1, arg2});
    }

    /**
     * Formats a localized value using the provided objects.
     *
     * @param key The identifier for the localized text to retrieve,
     * @param arg1 The object to use as {0} when formatting the localized text.
     * @param arg2 The object to use as {1} when formatting the localized text.
     * @param arg3 The object to use as {2} when formatting the localized text.
     * @return Formatted localized text.
     * @see #format(String, List)
     */
    public String format(String key, Object arg1, Object arg2, Object arg3)
    {
        return format(key, new Object[] {arg1, arg2, arg3});
    }

    /**
     * <p>Formats a localized value using the provided objects.</p>
     *
     * <p>ResourceBundle:
     * <blockquote><code><pre>
     * VelocityUsersNotWrong={0} out of {1} users can't be wrong!
     * </pre></code></blockquote>
     *
     * Template:
     * <blockquote><code><pre>
     * $l10n.format("VelocityUsersNotWrong", ["9", "10"])
     * </pre></code></blockquote>
     *
     * Result:
     * <blockquote><code><pre>
     * 9 out of 10 Velocity users can't be wrong!
     * </pre></code></blockquote></p>
     *
     * @param key The identifier for the localized text to retrieve,
     * @param args The objects to use as {0}, {1}, etc. when
     *             formatting the localized text.
     * @return Formatted localized text.
     */
    public String format(String key, List args)
    {
        return format(key, args.toArray());
    }


    /**
     * Formats a localized value using the provided objects.
     *
     * @param key The identifier for the localized text to retrieve,
     * @param args The <code>MessageFormat</code> data used when
     * formatting the localized text.
     * @return Formatted localized text.
     * @see #format(String, List)
     */
    public String format(String key, Object[] args)
    {
        String value = null;

        // we are going to allow html text within resource bundles.  This
        // avoids problems in translations when links or other html tags 
        // would result in an unnatural breakup of the text.  We need
        // to apply the filtering here on the arguments which might contain
        // user entered data, if we are going to skip the filtering later.
        for (int i=0; i<args.length; i++) 
        {
            Object obj = args[i];
            // we don't filter Number, because these are sometimes passed
            // to message formatter in order to make a choice.  Converting
            // the number to a String will cause error
            if (obj != null && 
                !(obj instanceof SkipFiltering) && 
                !(obj instanceof Number) 
                ) 
            {
                args[i] = ReferenceInsertionFilter.filter(obj.toString());
            }
        }

        try
        {
            value =super.format(key, args);
        }
        catch (MissingResourceException tryAgain)
        {
            String prefix = getPrefix(null);
            setPrefix(DEFAULT_SCOPE + '.');
            try
            {
                value = super.format(key, args);
            }
            catch (MissingResourceException itsNotThere)
            {
                value = "ERROR! Missing resource (" + key + ")";
                Log.get().error(
                    "ScarabLocalizationTool: ERROR! Missing resource: " + key);
            }
            setPrefix(prefix);
        }
        catch (Exception e)
        {
            value = "ERROR! Bad resource (" + key + ")";
            Log.get().error(
                "ScarabLocalizationTool: ERROR! Bad resource: " + key + 
                ".  See log for details.", e);
        }

        return value;
    }

    /**
     * Provides <code>$l10n.Title</code> to templates, grabbing it
     * from the <code>title</code> property for the current template.
     *
     * @return The title for the template used in the current request,
     * or the text <code>Scarab</code> if not set.
     */
    public String getTitle()
    {
        String title = findProperty(TITLE_PROP, false);
        if (title == null)
        {
            // Either the property name doesn't correspond to a
            // localization key, or the localization property pointed
            // to by the key doesn't have a value.  Try the default.
            title = findProperty(TITLE_PROP, true);

            // If no default localization this category of template
            // property was available, we return null so the VTL
            // renders literally and the problem can be detected.
        }
        return title;
    }

    /**
     * Retrieves the localized version of the value of
     * <code>property</code>.
     *
     * @param property The name of the property whose value to
     * retrieve.
     * @param useDefaultScope Whether or not to use the default scope
     * (defined by the <code>DEFAULT_SCOPE</code> constant).
     * @return The localized property value.
     */
    protected String findProperty(String property, boolean useDefaultScope)
    {
        String value = null;
        if (properties != null)
        {
            // $l10n.get($props.get($template, "title"))

            String templateName =
                (useDefaultScope ? DEFAULT_SCOPE : 
                 data.getTarget().replace(',', '/'));
            if (templateName == null)
            {
                templateName = DEFAULT_SCOPE;
            }
            String propName = "template." + templateName + '.' + property;
            String l10nKey = properties.getString(propName);
            Log.get().debug("ScarabLocalizationTool: Property name '" + propName +
                        "' -> localization key '" + l10nKey + '\'');

            if (l10nKey != null)
            {
                value = get(templateName + '.', l10nKey);
                Log.get().debug("ScarabLocalizationTool: Localized value is '" +
                            value + '\'');
            }
        }
        return value;
    }

    public void setBundlePrefix(String prefix)
    {
        oldBundlePrefix = bundlePrefix;
        bundlePrefix = prefix; 
    }

    public void restoreBundlePrefix()
    {
        bundlePrefix = oldBundlePrefix;
    }

    protected String getBundleName()
    {
        String name = null;
        if (bundlePrefix == null) 
        {
            name = Localization.getDefaultBundleName();
        }
        else 
        {
            name = bundlePrefix + Localization.getDefaultBundleName();
        }
        return name;
    }


    // ---- ApplicationTool implementation  ----------------------------------

    /**
     * Sets the localization prefix to the name of the target for the
     * current request plus dot (i.e. <code>Prefix.vm.</code>).
     */
    public void init(Object runData)
    {
        super.init(runData);
        if (runData instanceof RunData)
        {
            data = (RunData) runData;
            properties = Turbine.getConfiguration();
        }
    }

    public void refresh()
    {
        super.refresh();
        data = null;
        properties = null;
        bundlePrefix = null;
        oldBundlePrefix = null;
    }
}