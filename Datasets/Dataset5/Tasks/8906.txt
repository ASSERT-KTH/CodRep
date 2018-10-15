import org.eclipse.internal.xpand2.XpandTokens;

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.xpand.ui.editor.scanning;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.internal.xpand2.codeassist.XpandTokens;
import org.eclipse.jface.text.rules.ICharacterScanner;
import org.eclipse.jface.text.rules.IRule;
import org.eclipse.jface.text.rules.IToken;
import org.eclipse.jface.text.rules.MultiLineRule;
import org.eclipse.jface.text.rules.Token;
import org.eclipse.jface.text.rules.WhitespaceRule;

/**
 * 
 */
public class TemplateTagScanner extends AbstractXpandRuleBasedScanner {

    public TemplateTagScanner() {
        final List<IRule> rules = new ArrayList<IRule>();
        // Add rule for strings
        rules.add(new MultiLineRule("\"", "\"", string,'\\',true));
        rules.add(new MultiLineRule("'", "'", string,'\\',true));
        // Add rule for brackets
        rules.add(new IRule() {
            /*
             * (non-Javadoc)
             * 
             * @see org.eclipse.jface.text.rules.IRule#evaluate(org.eclipse.jface.text.rules.ICharacterScanner)
             */
            public IToken evaluate(final ICharacterScanner scanner) {
                final byte c = (byte) scanner.read();
                if (XpandTokens.LT_CHAR == c || XpandTokens.RT_CHAR == c)
                    return terminals;
                else {
                    scanner.unread();
                    return Token.UNDEFINED;
                }
            }
        });

        // Add rule for define
        rules.add(new KeywordRule(define, new String[] { XpandTokens.DEFINE, XpandTokens.ENDDEFINE,
                XpandTokens.AROUND, XpandTokens.ENDAROUND }));
        // Add rule for keywords
        rules.add(new KeywordRule(keyword, XpandTokens.ALLKEYWORDS));
        // Add generic whitespace rule.
        rules.add(new WhitespaceRule(new WhitespaceDetector()));

        setRules(rules.toArray(new IRule[rules.size()]));
    }

}
 No newline at end of file