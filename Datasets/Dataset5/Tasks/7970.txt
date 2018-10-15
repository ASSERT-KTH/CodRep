final FaceletDocumentFactory factory = new FaceletDocumentFactory(_project);

package org.eclipse.jst.jsf.facelet.ui.internal.hover;

import org.eclipse.core.resources.IProject;
import org.eclipse.jface.text.IRegion;
import org.eclipse.jface.text.ITextHover;
import org.eclipse.jface.text.ITextViewer;
import org.eclipse.jst.jsf.context.resolver.structureddocument.IStructuredDocumentContextResolverFactory;
import org.eclipse.jst.jsf.context.resolver.structureddocument.IWorkspaceContextResolver;
import org.eclipse.jst.jsf.context.resolver.structureddocument.internal.ITextRegionContextResolver;
import org.eclipse.jst.jsf.context.structureddocument.IStructuredDocumentContext;
import org.eclipse.jst.jsf.context.structureddocument.IStructuredDocumentContextFactory;
import org.eclipse.jst.jsf.facelet.core.internal.cm.FaceletDocumentFactory;
import org.eclipse.jst.jsf.ui.internal.jspeditor.JSFELHover;
import org.eclipse.wst.html.ui.internal.taginfo.HTMLTagInfoHoverProcessor;
import org.eclipse.wst.xml.core.internal.contentmodel.CMElementDeclaration;
import org.eclipse.wst.xml.core.internal.regions.DOMRegionContext;
import org.w3c.dom.Element;
import org.w3c.dom.Node;

public class FaceletHover implements ITextHover
{
    private IProject                  _project;
    private JSFELHover                _elHover;
    private HTMLTagInfoHoverProcessor _htmlHoverProcessor;

    public FaceletHover()
    {
        _elHover = new JSFELHover();
        _htmlHoverProcessor = new MyHTMLTagInfoHoverProcessor();
    }

    public String getHoverInfo(ITextViewer textViewer, IRegion hoverRegion)
    {
        final IStructuredDocumentContext context = IStructuredDocumentContextFactory.INSTANCE
                .getContext(textViewer, hoverRegion.getOffset());
        String info = null;
        if (isInAttributeValue(context))
        {
            info = _elHover.getHoverInfo(textViewer, hoverRegion);
        }

        if (info == null)
        {
            if (context != null)
            {
                _project = getProject(context);
            }

            info = _htmlHoverProcessor.getHoverInfo(textViewer, hoverRegion);
        }

        return info;
    }

    public IRegion getHoverRegion(ITextViewer textViewer, int offset)
    {
        IRegion region = null;
        final IStructuredDocumentContext context = IStructuredDocumentContextFactory.INSTANCE
                .getContext(textViewer, offset);

        // if we are in an attribute value, try to get a region from the
        // el hover first
        if (context != null)
        {
            if (isInAttributeValue(context))
            {
                region = _elHover.getHoverRegion(textViewer, offset);
            }
        }

        if (region == null)
        {
            if (context != null)
            {
                _project = getProject(context);
            }
            region = _htmlHoverProcessor.getHoverRegion(textViewer, offset);
        }

        return region;
    }

    private boolean isInAttributeValue(final IStructuredDocumentContext context)
    {
        final ITextRegionContextResolver resolver = IStructuredDocumentContextResolverFactory.INSTANCE
                .getTextRegionResolver(context);
        final String regionType = resolver.getRegionType();
        if (regionType != null
                && (regionType == DOMRegionContext.XML_TAG_ATTRIBUTE_VALUE || resolver
                        .matchesRelative(new String[]
                        { DOMRegionContext.XML_TAG_ATTRIBUTE_VALUE })))
        {
            return true;
        }

        return false;
    }

    private IProject getProject(final IStructuredDocumentContext context)
    {
        final IWorkspaceContextResolver resolver = IStructuredDocumentContextResolverFactory.INSTANCE
                .getWorkspaceContextResolver(context);

        if (resolver != null)
        {
            return resolver.getProject();
        }
        return null;
    }

    private class MyHTMLTagInfoHoverProcessor extends HTMLTagInfoHoverProcessor
    {
        @Override
        protected CMElementDeclaration getCMElementDeclaration(Node node)
        {
            if (_project != null && node.getNodeType() == Node.ELEMENT_NODE
                    && node.getPrefix() != null)
            {
                final Element element = (Element) node;
                final FaceletDocumentFactory factory = new FaceletDocumentFactory();

                final CMElementDeclaration elementDecl = factory
                        .createCMElementDeclaration(_project, element);

                if (elementDecl != null)
                {
                    return elementDecl;
                }
            }

            return super.getCMElementDeclaration(node);
        }
    }
}