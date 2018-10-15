else if (DefaultTagTypeInfo.isDefaultLib(tagId.getUri()))

package org.eclipse.jst.jsf.facelet.core.internal.registry;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.resources.IProject;
import org.eclipse.jst.jsf.common.dom.TagIdentifier;
import org.eclipse.jst.jsf.common.runtime.internal.model.component.ComponentTypeInfo;
import org.eclipse.jst.jsf.common.runtime.internal.model.decorator.ConverterTypeInfo;
import org.eclipse.jst.jsf.common.runtime.internal.model.decorator.ValidatorTypeInfo;
import org.eclipse.jst.jsf.common.runtime.internal.model.types.TypeInfo;
import org.eclipse.jst.jsf.common.runtime.internal.view.model.common.ITagElement;
import org.eclipse.jst.jsf.common.runtime.internal.view.model.common.IHandlerTagElement.TagHandlerType;
import org.eclipse.jst.jsf.core.JSFVersion;
import org.eclipse.jst.jsf.core.internal.tld.TagIdentifierFactory;
import org.eclipse.jst.jsf.core.jsfappconfig.JSFAppConfigUtils;
import org.eclipse.jst.jsf.designtime.internal.view.model.jsp.AbstractTagResolvingStrategy;
import org.eclipse.jst.jsf.designtime.internal.view.model.jsp.DefaultTagTypeInfo;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.ComponentTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.ConverterTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.HandlerTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.IFaceletTagConstants;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.NoArchetypeFaceletTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.ValidatorTag;
import org.eclipse.wst.common.project.facet.core.IProjectFacetVersion;

public class VeryTemporaryDefaultFaceletResolver extends
        AbstractTagResolvingStrategy<FaceletTagElement, String>
{
    public final static String       ID = "org.eclipse.jst.jsf.facelet.core.VeryTemporaryDefaultFaceletResolver";
    private final DefaultTagTypeInfo _coreHtmlTypeInfo;
    private final IProject           _project;

    public VeryTemporaryDefaultFaceletResolver(final IProject project)
    {
        super();
        _project = project;
        _coreHtmlTypeInfo = new DefaultTagTypeInfo();
    }

    @Override
    public final String getId()
    {
        return ID;
    }

    @Override
    public ITagElement resolve(final FaceletTagElement element)
    {
        final IProjectFacetVersion version = JSFAppConfigUtils
                .getProjectFacet(_project);
        final String versionAsString = version.getVersionString();
        final JSFVersion jsfVersion = JSFVersion.valueOfString(versionAsString);

        final String uri = element.getUri();
        final String name = element.getName();
        final TagIdentifier tagId = TagIdentifierFactory.createJSPTagWrapper(
                uri, name);
        TypeInfo typeInfo = null;
        if (IFaceletTagConstants.URI_JSF_FACELETS.equals(element.getUri()))
        {
            typeInfo = getTypeInfo(tagId, jsfVersion);
        }
        else
        {
            typeInfo = _coreHtmlTypeInfo.getTypeInfo(tagId,
                    jsfVersion);
        }
        return createFromTypeInfo(tagId, typeInfo);
    }

    private ITagElement createFromTypeInfo(final TagIdentifier tagId,
            final TypeInfo typeInfo)
    {
        if (typeInfo instanceof ComponentTypeInfo)
        {
            return new ComponentTag(tagId.getUri(), tagId.getTagName(),
                    (ComponentTypeInfo) typeInfo);
        }
        else if (typeInfo instanceof ConverterTypeInfo)
        {
            return new ConverterTag(tagId.getUri(), tagId.getTagName(),
                    (ConverterTypeInfo) typeInfo, null);
        }
        else if (typeInfo instanceof ValidatorTypeInfo)
        {
            return new ValidatorTag(tagId.getUri(), tagId.getTagName(),
                    (ValidatorTypeInfo) typeInfo, null);
        }
        else if (typeInfo instanceof TagHandlerType)
        {
            return new HandlerTag(tagId.getUri(), tagId.getTagName(),
                    (TagHandlerType) typeInfo, null);
        }
        else if (_coreHtmlTypeInfo.isDefaultLib(tagId.getUri()))
        {
            return new NoArchetypeFaceletTag(tagId.getUri(), tagId.getTagName());
        }

        // not found
        return null;

    }

    public final String getDisplayName()
    {
        return "Meta-data Driven Tag Resolver";
    }

    private static final ComponentTypeInfo COMPINFO_COMPONENT = new ComponentTypeInfo(
                                                                      "facelets.ui.ComponentRef",
                                                                      "com.sun.facelets.tag.ui.ComponentRef",
                                                                      new String[]
                                                                      {
            "javax.faces.component.UIComponentBase",
            "javax.faces.component.UIComponent", "java.lang.Object", },
                                                                      new String[]
                                                                      { "javax.faces.component.StateHolder" },
                                                                      "facelets",
                                                                      null);

    private static final ComponentTypeInfo COMPINFO_DEBUG     = new ComponentTypeInfo(
                                                                      "facelets.ui.Debug",
                                                                      "com.sun.facelets.tag.ui.UIDebug",
                                                                      new String[]
                                                                      {
            "javax.faces.component.UIComponentBase",
            "javax.faces.component.UIComponent", "java.lang.Object", },
                                                                      new String[]
                                                                      { "javax.faces.component.StateHolder" },
                                                                      "facelets",
                                                                      null);

    private static final ComponentTypeInfo COMPINFO_REPEAT    = new ComponentTypeInfo(
                                                                      "facelets.ui.Repeat",
                                                                      "com.sun.facelets.component.UIRepeat",
                                                                      new String[]
                                                                      {
            "javax.faces.component.UIComponentBase",
            "javax.faces.component.UIComponent", "java.lang.Object", },
                                                                      new String[]
                                                                      {
            "javax.faces.component.StateHolder",
            "javax.faces.component.NamingContainer"                  },
                                                                      "facelets",
                                                                      null);
    
    /**
     * @param tagId
     * @param jsfVersion
     * @return a type info for the tag id in jsf version or null if none.
     */
    private TypeInfo getTypeInfo(final TagIdentifier tagId,
            final JSFVersion jsfVersion)
    {

        switch (jsfVersion)
        {
            case V1_0:
            case V1_1:
                return JSF11_ELEMENTS.get(tagId);

            case V1_2:
                return JSF12_ELEMENTS.get(tagId);

            default:
                return null;
        }
    }
    private static Map<TagIdentifier, TypeInfo> JSF11_ELEMENTS;
    private static Map<TagIdentifier, TypeInfo> JSF12_ELEMENTS;
    static
    {
        final Map<TagIdentifier, TypeInfo> elements = new HashMap<TagIdentifier, TypeInfo>();

        elements.put(IFaceletTagConstants.TAG_IDENTIFIER_COMPONENT,
                COMPINFO_COMPONENT);

        elements.put(IFaceletTagConstants.TAG_IDENTIFIER_DEBUG,
                COMPINFO_DEBUG);

        elements.put(IFaceletTagConstants.TAG_IDENTIFIER_FRAGMENT,
                COMPINFO_COMPONENT);

        elements.put(IFaceletTagConstants.TAG_IDENTIFIER_REPEAT,
                COMPINFO_REPEAT);

        JSF11_ELEMENTS = Collections.unmodifiableMap(elements);

        JSF12_ELEMENTS = Collections
                .unmodifiableMap(new HashMap<TagIdentifier, TypeInfo>(elements));
    }
}