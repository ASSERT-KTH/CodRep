if (template.matches(prefix, contextTypeId)) {

/*******************************************************************************
 * Copyright (c) 2008, 2009 28msec Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Gabriel Petrovay (28msec) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.internal.ui.templates;

import org.eclipse.core.resources.IProject;
import org.eclipse.dltk.ui.templates.ScriptTemplateAccess;
import org.eclipse.dltk.ui.templates.ScriptTemplateCompletionProcessor;
import org.eclipse.dltk.ui.text.completion.ScriptContentAssistInvocationContext;
import org.eclipse.jface.text.BadLocationException;
import org.eclipse.jface.text.IDocument;
import org.eclipse.jface.text.ITextViewer;
import org.eclipse.jface.text.templates.Template;
import org.eclipse.jface.text.templates.TemplateContext;
import org.eclipse.jface.text.templates.TemplateContextType;
import org.eclipse.wst.xquery.core.IXQDTLanguageConstants;
import org.eclipse.wst.xquery.core.codeassist.IXQDTCompletionConstants;
import org.eclipse.wst.xquery.core.text.XQDTWordDetector;
import org.eclipse.wst.xquery.core.utils.LanguageUtil;

public class XQDTTemplateCompletionProcessor extends ScriptTemplateCompletionProcessor {

    // private static final class ProposalComparator implements Comparator<TemplateProposal> {
    //
    // public int compare(TemplateProposal o1, TemplateProposal o2) {
    // return o2.getRelevance() - o1.getRelevance();
    // }
    // }
    //
    // private static final Comparator<TemplateProposal> comparator = new ProposalComparator();

    private boolean fIsNormalPrefixType;

    public XQDTTemplateCompletionProcessor(ScriptContentAssistInvocationContext context) {
        super(context);
    }

    protected String getContextTypeId() {
        IProject project = getContext().getProject().getProject();
        int mask = LanguageUtil.getLanguageLevel(project);

        if (LanguageUtil.isLanguage(mask, IXQDTLanguageConstants.LANGUAGE_XQUERY_SCRIPTING)) {
            return XQueryScriptingTemplateContentType.CONTEXT_TYPE_ID;
        } else if (LanguageUtil.isLanguage(mask, IXQDTLanguageConstants.LANGUAGE_XQUERY_UPDATE)) {
            return XQueryUpdateTemplateContentType.CONTEXT_TYPE_ID;
        }
        return XQueryTemplateContentType.CONTEXT_TYPE_ID;
    }

    protected ScriptTemplateAccess getTemplateAccess() {
        return XQDTTemplateAccess.getInstance();
    }

    @Override
    protected boolean isValidPrefix(String prefix) {
        return fIsNormalPrefixType;
    }

    protected boolean isMatchingTemplate(Template template, String prefix, TemplateContext context) {
        if (template.getName().equals("function")) {
            System.err
                    .println("Move potential functions away from normal template processing: XQDTTemplateCompletionProcessor");
            // XQDTTemplateContext tc = (XQDTTemplateContext)context;
            // try {
            // if (tc.getSourceModule().getElementAt(tc.getCompletionOffset()) != null)
            // return false;
            // } catch (ModelException e) {
            // return false;
            // }
        }
        // else
        if (!template.getName().startsWith(prefix)) {
            return false;
        }

        if (template.matches(prefix, context.getContextType().getId())) {
            return true;
        } else {
            TemplateContextType contextType = context.getContextType();
            if (contextType instanceof XQueryTemplateContentType) {
                String[] alsoMatches = ((XQueryTemplateContentType)contextType).getCompatibleContentTypes();
                for (String contextTypeId : alsoMatches) {
                    if (template.getContextTypeId().equals(contextTypeId)) {
                        return true;
                    }
                }
            }
        }

        return false;
    }

    @Override
    protected String extractPrefix(ITextViewer viewer, int offset) {
        int i = offset;
        IDocument document = viewer.getDocument();
        if (i > document.getLength()) {
            return "";
        }

        XQDTWordDetector wd = new XQDTWordDetector();

        try {
            char ch = 0;

            while (i > 0) {
                ch = document.getChar(i - 1);
                if (!wd.isWordPart(ch)) {
                    break;
                }
                i--;
            }

            if (ch == ':' || ch == '$') {
                fIsNormalPrefixType = false;
            } else {
                fIsNormalPrefixType = true;
            }

            return document.get(i, offset - i);
        } catch (BadLocationException e) {
            return "";
        }
    }

    @Override
    protected int getRelevance(Template template, String prefix) {
        if (template.getName().startsWith(prefix)) {
            return IXQDTCompletionConstants.RELEVANCE_TEMPLATE;
        }
        return 0;
    }
}