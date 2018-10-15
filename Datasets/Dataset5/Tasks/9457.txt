(ComponentTypeInfo) elementType, null, _factory,

/*******************************************************************************
 * Copyright (c) 2008 Oracle Corporation.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Cameron Bateman - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.jsf.facelet.core.internal.registry;

import java.util.Iterator;

import org.eclipse.core.resources.IProject;
import org.eclipse.emf.common.util.EList;
import org.eclipse.jst.jsf.common.dom.TagIdentifier;
import org.eclipse.jst.jsf.common.runtime.internal.model.component.ComponentTypeInfo;
import org.eclipse.jst.jsf.common.runtime.internal.model.decorator.ConverterTypeInfo;
import org.eclipse.jst.jsf.common.runtime.internal.model.decorator.ValidatorTypeInfo;
import org.eclipse.jst.jsf.common.runtime.internal.model.types.TypeInfo;
import org.eclipse.jst.jsf.common.runtime.internal.view.model.common.ITagElement;
import org.eclipse.jst.jsf.common.runtime.internal.view.model.common.IHandlerTagElement.TagHandlerType;
import org.eclipse.jst.jsf.core.internal.tld.TagIdentifierFactory;
import org.eclipse.jst.jsf.designtime.internal.Messages;
import org.eclipse.jst.jsf.designtime.internal.view.mapping.ViewMetadataLoader;
import org.eclipse.jst.jsf.designtime.internal.view.mapping.ViewMetadataMapper;
import org.eclipse.jst.jsf.designtime.internal.view.mapping.viewmapping.TagMapping;
import org.eclipse.jst.jsf.designtime.internal.view.mapping.viewmapping.TagToViewObjectMapping;
import org.eclipse.jst.jsf.designtime.internal.view.model.jsp.AbstractTagResolvingStrategy;
import org.eclipse.jst.jsf.designtime.internal.view.model.jsp.DefaultTagTypeInfo;
import org.eclipse.jst.jsf.facelet.core.internal.cm.FaceletDocumentFactory;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.ComponentTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.ConverterTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.HandlerTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.NoArchetypeFaceletTag;
import org.eclipse.jst.jsf.facelet.core.internal.tagmodel.ValidatorTag;
import org.osgi.framework.Version;

/**
 * Resolves facelet tags from JSF framework metadata.
 * 
 * @author cbateman
 *
 */
public class FaceletMetaResolvingStrategy
        extends
        AbstractTagResolvingStrategy<IFaceletTagResolvingStrategy.TLDWrapper, String>
        implements IFaceletTagResolvingStrategy
{

    /**
     * strategy id
     */
    public final static String           ID           = "org.eclipse.jst.jsf.facelet.metadata.FaceletMetaResolvingStrategy"; //$NON-NLS-1$
    /**
     * displayable nameb
     */
    public final static String           DISPLAY_NAME = Messages.DefaultJSPTagResolver_DisplayName;

    private final ViewMetadataLoader     _loader;
    private final ViewMetadataMapper     _mapper;
    private final FaceletDocumentFactory _factory;

    /**
     * @param project
     * @param factory 
     */
    public FaceletMetaResolvingStrategy(final IProject project,
            final FaceletDocumentFactory factory)
    {
        _factory = factory;
        _loader = new ViewMetadataLoader(project);
        _mapper = new ViewMetadataMapper();
    }

    @Override
    public ITagElement resolve(
            final IFaceletTagResolvingStrategy.TLDWrapper elementDecl)
    {
        // final IProjectFacetVersion version = JSFAppConfigUtils
        // .getProjectFacet(_project);
        // final String versionAsString = version.getVersionString();
        // final JSFVersion jsfVersion =
        // JSFVersion.valueOfString(versionAsString);

        final String uri = elementDecl.getUri();
        final String tagName = elementDecl.getTagDefn().getName();
        final TagIdentifier tagId = TagIdentifierFactory.createJSPTagWrapper(
                uri, tagName);
        // final DefaultTagTypeInfo defaultTagTypeInfo = new
        // DefaultTagTypeInfo();
        final TagMapping mapping = _loader.getTagToViewMapping(tagId);

        TypeInfo elementType = null;
        if (mapping != null)
        {
            elementType = findTypeInfo(mapping, "1.1", null); //$NON-NLS-1$
        }

        if (elementType instanceof ComponentTypeInfo)
        {
            return new ComponentTag(uri, tagName,
                    (ComponentTypeInfo) elementType, _factory,
                    new MetadataAttributeAdvisor(tagId, _loader));
        }
        else if (elementType instanceof ConverterTypeInfo)
        {
            return new ConverterTag(uri, tagName,
                    (ConverterTypeInfo) elementType, null, _factory,
                    new MetadataAttributeAdvisor(tagId, _loader));
        }
        else if (elementType instanceof ValidatorTypeInfo)
        {
            return new ValidatorTag(uri, tagName,
                    (ValidatorTypeInfo) elementType, null, _factory,
                    new MetadataAttributeAdvisor(tagId, _loader));
        }
        else if (elementType instanceof TagHandlerType)
        {
            return new HandlerTag(uri, tagName,
                    (TagHandlerType) elementType, null, _factory,
                    new MetadataAttributeAdvisor(
                            tagId, _loader));
        }
        else if (DefaultTagTypeInfo.isDefaultLib(tagId.getUri()))
        {
            return new NoArchetypeFaceletTag(uri, tagName, _factory, new MetadataAttributeAdvisor(tagId, _loader));
        }

        // not found
        return null;
    }

    private TypeInfo findTypeInfo(final TagMapping mapping,
            final String jsfVersion, final String libVersion)
    {
        final EList list = mapping.getVersionedTagToViewMappings();

        FIND_BY_VERSION: for (final Iterator<?> it = list.iterator(); it
                .hasNext();)
        {
            Object obj = it.next();

            if (obj instanceof TagToViewObjectMapping)
            {
                final TagToViewObjectMapping viewMapping = (TagToViewObjectMapping) obj;

                final String minJsfVersionString = viewMapping
                        .getMinJSFVersion();
                if (minJsfVersionString != null)
                {
                    try
                    {
                        final Version version = new Version(jsfVersion);
                        final Version minVersion = Version
                                .parseVersion(minJsfVersionString);

                        if (version.compareTo(minVersion) < 0)
                        {
                            // my version is less than the minimum specified
                            // by this meta-data
                            continue FIND_BY_VERSION;
                        }
                    }
                    catch (final IllegalArgumentException iae)
                    {
                        continue FIND_BY_VERSION;
                    }
                }
                final String minLibVersionString = viewMapping
                        .getMinLibraryVersion();
                if (libVersion != null && minLibVersionString != null)
                {
                    try
                    {
                        final Version version = new Version(libVersion);
                        final Version minLibVersion = Version
                                .parseVersion(minLibVersionString);

                        if (version.compareTo(minLibVersion) < 0)
                        {
                            // my lib version is less than the minimum specified
                            // by the meta-data
                            continue FIND_BY_VERSION;
                        }
                    }
                    catch (IllegalArgumentException iae)
                    {
                        continue FIND_BY_VERSION;
                    }
                }
                return _mapper.mapToFrameworkData(viewMapping.getTypeInfo());
            }
        }
        return null;
    }

    @Override
    public String getId()
    {
        return ID;
    }

    public String getDisplayName()
    {
        return DISPLAY_NAME;
    }

}