import org.eclipse.wst.xquery.core.codeassist.IXQDTCompletionConstants.CompletionPrefixType;

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
package org.eclipse.wst.xquery.internal.ui.text.codeassist;

import org.eclipse.dltk.ui.DLTKPluginImages;
import org.eclipse.dltk.ui.templates.ScriptTemplateAccess;
import org.eclipse.dltk.ui.text.completion.ScriptContentAssistInvocationContext;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.wst.xquery.internal.core.codeassist.XQDTCompletionEngine.CompletionPrefixType;
import org.eclipse.wst.xquery.internal.ui.templates.XQDTStringTemplateAccess;
import org.eclipse.wst.xquery.internal.ui.templates.XQDTStringTemplateContentType;

public class XQDTStringTemplateCompletionProcessor extends XQDTPrefixedTemplateCompletionProcessor {

    public XQDTStringTemplateCompletionProcessor(ScriptContentAssistInvocationContext context) {
        super(context);
    }

    protected String getContextTypeId() {
        return XQDTStringTemplateContentType.CONTEXT_TYPE_ID;
    }

    protected ScriptTemplateAccess getTemplateAccess() {
        return XQDTStringTemplateAccess.getInstance();
    }

    @Override
    protected ImageDescriptor getImageDescriptor() {
        return DLTKPluginImages.DESC_OBJS_KEYWORD;
    }

    @Override
    protected boolean isValidPrefix(String prefix) {
        return ("#".startsWith(prefix) && fPrefixType == CompletionPrefixType.AMPERSAND);
    }

}