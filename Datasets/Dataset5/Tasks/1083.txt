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

import org.eclipse.dltk.ui.templates.ScriptTemplateAccess;
import org.eclipse.dltk.ui.text.completion.ScriptContentAssistInvocationContext;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.wst.xquery.internal.core.codeassist.XQDTCompletionEngine.CompletionPrefixType;
import org.eclipse.wst.xquery.internal.ui.XQDTImages;
import org.eclipse.wst.xquery.internal.ui.templates.XPathFunctionContentType;
import org.eclipse.wst.xquery.internal.ui.templates.XQDTFnFunctionTemplateAccess;

public class XQDTFnFunctionCompletionProcessor extends XQDTPrefixedTemplateCompletionProcessor {

    public XQDTFnFunctionCompletionProcessor(ScriptContentAssistInvocationContext context) {
        super(context);
    }

    @Override
    protected String getContextTypeId() {
        return XPathFunctionContentType.CONTEXT_TYPE_ID;
    }

    @Override
    protected ScriptTemplateAccess getTemplateAccess() {
        return XQDTFnFunctionTemplateAccess.getInstance();
    }

    @Override
    protected boolean isValidPrefix(String prefix) {
        return fPrefixPrefix == null || (fPrefixPrefix.equals("fn") && fPrefixType == CompletionPrefixType.COLON);
    }

    @Override
    protected ImageDescriptor getImageDescriptor() {
        return XQDTImages.DESC_ELCL_FN_PROPOSAL;
    }

}
 No newline at end of file