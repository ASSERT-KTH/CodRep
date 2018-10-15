public class ProposalFactoryDefaultImpl extends AbstractProposalFactory {

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

package org.eclipse.internal.xtend.expression.codeassist;

import org.eclipse.internal.xtend.xtend.ast.Extension;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.typesystem.Operation;
import org.eclipse.xtend.typesystem.Property;
import org.eclipse.xtend.typesystem.StaticProperty;
import org.eclipse.xtend.typesystem.Type;

public class ProposalFactoryDefaultImpl extends AbstractProposalFactory implements ProposalFactory {

	public Object createPropertyProposal(final Property p, final String prefix, final boolean onCollection) {
		return new ProposalImpl(prefix, p.getName(), p.toString(), p);
	}

	public Object createStaticPropertyProposal(final StaticProperty p, final String prefix, final boolean onCollection) {
		return new ProposalImpl(prefix, p.getName(), p.toString(), p);
	}

	public Object createOperationProposal(final Operation p, final String prefix, final boolean onCollection) {
		return new ProposalImpl(prefix, p.getName(), p.toString(), p);
	}

	public Object createExtensionOnMemberPositionProposal(final Extension p, final String prefix,
			final boolean onCollection) {
		return new ProposalImpl(prefix, p.getName(), p.toString(), p);
	}

	public Object createCollectionSpecificOperationProposal(final String insertString, final String displayString,
			final String prefix, final int cursor, final int marked) {
		return new ProposalImpl(prefix, insertString, displayString, displayString);
	}

	public Object createExtensionProposal(final Extension p, final String prefix) {
		return new ProposalImpl(prefix, p.getName(), p.toString(), p);
	}

	public Object createVariableProposal(final String name, final Type t, final String prefix) {
		return new ProposalImpl(prefix, name, name, new Variable(name, t));
	}

	public Object createTypeProposal(final String insertString, final Type type, final String prefix) {
		return new ProposalImpl(prefix, insertString, type.getName(), type);
	}

	public Object createStatementProposal(final String insertString, final String displayString, final String prefix,
			final int cursor, final int marked) {
		return new ProposalImpl(prefix, insertString, displayString, displayString);
	}

	public Object createStatementProposal(final String insertString, final String displayString, final String prefix) {
		return new ProposalImpl(prefix, insertString, displayString, displayString);
	}

	public Object createKeywordProposal(final String insertString, final String displayString, final String prefix) {
		return new ProposalImpl(prefix, insertString, displayString, displayString);
	}

	public Object createExtensionImportProposal(String insertStr, String displayStr, String prefix, int cursor,
			int marked) {
		return new ProposalImpl(prefix, insertStr, displayStr, displayStr);
	}

	public Object createNamespaceProposal(String insertStr, String displayStr, String prefix) {
		return new ProposalImpl(prefix, insertStr, displayStr, displayStr);
	}

	public Object createDefinitionProposal(String insertStr, String displayStr, String prefix) {
		return new ProposalImpl(prefix, insertStr, displayStr, displayStr);
	}

}