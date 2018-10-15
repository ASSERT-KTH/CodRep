typeInfo = DTComponentIntrospector.getComponent(componentType,

package org.eclipse.jst.jsf.facelet.core.internal.registry;

import org.eclipse.core.resources.IProject;
import org.eclipse.jem.internal.proxy.core.IConfigurationContributor;
import org.eclipse.jst.jsf.common.dom.TagIdentifier;
import org.eclipse.jst.jsf.common.runtime.internal.model.component.ComponentTypeInfo;
import org.eclipse.jst.jsf.common.runtime.internal.model.decorator.ConverterTypeInfo;
import org.eclipse.jst.jsf.common.runtime.internal.model.decorator.ValidatorTypeInfo;
import org.eclipse.jst.jsf.common.runtime.internal.view.model.common.ITagElement;
import org.eclipse.jst.jsf.core.internal.tld.TagIdentifierFactory;
import org.eclipse.jst.jsf.designtime.internal.view.DTComponentIntrospector;
import org.eclipse.jst.jsf.designtime.internal.view.mapping.ViewMetadataLoader;
import org.eclipse.jst.jsf.designtime.internal.view.model.jsp.AbstractTagResolvingStrategy;
import org.eclipse.jst.jsf.designtime.internal.view.model.jsp.IAttributeAdvisor;
import org.eclipse.jst.jsf.facelet.core.internal.cm.FaceletDocumentFactory;
import org.eclipse.jst.jsf.facelet.core.internal.registry.taglib.faceletTaglib.ComponentTagDefn;
import org.eclipse.jst.jsf.facelet.core.internal.registry.taglib.faceletTaglib.ConverterTagDefn;
import org.eclipse.jst.jsf.facelet.core.internal.registry.taglib.faceletTaglib.HandlerTagDefn;
import org.eclipse.jst.jsf.facelet.core.internal.registry.taglib.faceletTaglib.SourceTagDefn;
import org.eclipse.jst.jsf.facelet.core.internal.registry.taglib.faceletTaglib.TagDefn;
import org.eclipse.jst.jsf.facelet.core.internal.registry.taglib.faceletTaglib.ValidatorTagDefn;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.ComponentTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.ConverterTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.FaceletTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.HandlerTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.NoArchetypeFaceletTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.SourceTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.ValidatorTag;

/*package*/class FaceletTagResolvingStrategy
        extends
        AbstractTagResolvingStrategy<IFaceletTagResolvingStrategy.TLDWrapper, String>
        implements IFaceletTagResolvingStrategy
{
    public final static String           ID = "org.eclipse.jst.jsf.facelet.core.FaceletTagResolvingStrategy"; //$NON-NLS-1$
    private final IProject               _project;
    private final FaceletDocumentFactory _factory;
    private final ViewMetadataLoader     _viewLoader;

    public FaceletTagResolvingStrategy(final IProject project,
            final FaceletDocumentFactory factory)
    {
        _project = project;
        _factory = factory;
        _viewLoader = new ViewMetadataLoader(project);
    }

    @Override
    public final String getId()
    {
        return ID;
    }

    @Override
    public final ITagElement resolve(final TLDWrapper tldWrapper)
    {
        return createFaceletTag(tldWrapper.getUri(), tldWrapper.getTagDefn());
    }

    public final String getDisplayName()
    {
        return Messages.FaceletTagResolvingStrategy_FACELET_TAG_RESOLVER_DISPLAY_NAME;
    }

    private FaceletTag createFaceletTag(final String uri, final TagDefn tagDefn)
    {
        final String tagName = tagDefn.getName();
        final TagIdentifier tagId = TagIdentifierFactory.createJSPTagWrapper(
                uri, tagName);

        final IAttributeAdvisor advisor = new MetadataAttributeAdvisor(tagId,
                _viewLoader);

        if (tagDefn instanceof ComponentTagDefn)
        {
            final ComponentTagDefn componentTagDefn = (ComponentTagDefn) tagDefn;
            final String componentType = componentTagDefn.getComponentType();
            final String componentClass = DTComponentIntrospector
                    .findComponentClass(componentType, _project);

            ComponentTypeInfo typeInfo = null;

            if (componentClass != null)
            {
                typeInfo = DTComponentIntrospector.getComponent(componentClass,
                        componentClass, _project,
                        new IConfigurationContributor[]
                        { new ELProxyContributor(_project) });
            }
            return new ComponentTag(uri, tagName, typeInfo, safeGetString(componentTagDefn.getHandlerClass()), _factory, advisor);
        }
        // render type is optional, but must have component type
        else if (tagDefn instanceof ValidatorTagDefn)
        {
            final ValidatorTagDefn validatorTagDefn = (ValidatorTagDefn) tagDefn;
            final String validatorId = validatorTagDefn.getValidatorId();

            ValidatorTypeInfo typeInfo;

            if (validatorId != null)
            {
                final String validatorClass = DTComponentIntrospector
                        .findValidatorClass(validatorId, _project);
                typeInfo = new ValidatorTypeInfo(validatorClass, validatorId);
            }
            else
            {
                typeInfo = ValidatorTypeInfo.UNKNOWN;
            }

            return new ValidatorTag(uri, tagName, typeInfo, safeGetString(validatorTagDefn.getHandlerClass()), _factory,
                    advisor);
        }
        // render type is optional, but must have converter id
        else if (tagDefn instanceof ConverterTagDefn)
        {
            final ConverterTagDefn converterTagDefn = (ConverterTagDefn) tagDefn;
            final String converterId = converterTagDefn.getConverterId();

            ConverterTypeInfo typeInfo;

            if (converterId != null)
            {
                final String converterClass = DTComponentIntrospector
                        .findConverterClass(converterId, _project);
                typeInfo = new ConverterTypeInfo(converterClass, converterId);
            }
            else
            {
                typeInfo = ConverterTypeInfo.UNKNOWN;
            }

            // for now, all converters are unknown
            return new ConverterTag(uri, tagName, typeInfo, 
                    safeGetString(converterTagDefn.getHandlerClass()), _factory, advisor);
        }
        else if (tagDefn instanceof HandlerTagDefn)
        {
            final String handlerClass = safeGetString(((HandlerTagDefn)tagDefn).getHandlerClass());
            return new HandlerTag(uri, tagName, null, handlerClass, _factory, advisor);
        }
        else if (tagDefn instanceof SourceTagDefn)
        {
            final String source = ((SourceTagDefn)tagDefn).getSource();
            return new SourceTag(uri, tagName, source, _factory, advisor);
        }

        return new NoArchetypeFaceletTag(uri, tagName, _factory, advisor);
    }
    
    private static String safeGetString(final String value)
    {
        if (value == null)
        {
            return null;
        }
        
        final String trimmed = value.trim();
        
        if ("".equals(trimmed)) //$NON-NLS-1$
        {
            return null;
        }
        
        return trimmed;
    }
}