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
import org.eclipse.jface.text.rules.IPredicateRule;
import org.eclipse.jface.text.rules.IRule;
import org.eclipse.jface.text.rules.IToken;
import org.eclipse.jface.text.rules.MultiLineRule;
import org.eclipse.jface.text.rules.RuleBasedPartitionScanner;
import org.eclipse.jface.text.rules.Token;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * 
 * 
 */
public class XpandPartitionScanner extends RuleBasedPartitionScanner {
    public final static String TAG = "__tag";

    public final static String COMMENT = "__comment";

    public XpandPartitionScanner() {

        final IToken tag = new Token(TAG);
        final IToken comment = new Token(COMMENT);

        final List<IRule> rules = new ArrayList<IRule>();

        // TODO we need to handle whitespace like this: '<< REM .... ENDREM >>'
		rules.add(new MultiLineRule(XpandTokens.LT + XpandTokens.REM, XpandTokens.ENDREM + XpandTokens.RT, comment,
				(char) 0, true));
		rules.add(new MultiLineRule(XpandTokens.LT + XpandTokens.REM, XpandTokens.ENDREM + "-" + XpandTokens.RT,
				comment, (char) 0, true));

        rules.add(new MultiLineRule(XpandTokens.LT, XpandTokens.RT, tag));

		setPredicateRules(rules.toArray(new IPredicateRule[rules.size()]));
    }
}