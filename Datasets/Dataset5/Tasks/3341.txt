return true;

/*******************************************************************************
 * Copyright (c) 2005 - 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/
package org.eclipse.xtend.shared.ui.editor.search.query;

import java.util.List;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.OperationCanceledException;
import org.eclipse.core.runtime.Status;
import org.eclipse.search.ui.ISearchQuery;
import org.eclipse.search.ui.ISearchResult;
import org.eclipse.search.ui.text.AbstractTextSearchResult;
import org.eclipse.search.ui.text.Match;
import org.eclipse.xtend.shared.ui.Messages;
import org.eclipse.xtend.shared.ui.core.IXtendXpandProject;
import org.eclipse.xtend.shared.ui.core.search.SearchMatch;

import com.ibm.icu.text.MessageFormat;

/**
 * <code>XtendXpandSearchQuery</code> is a base class for search queries. Queries
 * contain the search parameters for the search and the code that performs the
 * query as well.
 * 
 * @author Peter Friese
 */
public abstract class XtendXpandSearchQuery implements ISearchQuery {

	private final String identifier;
	private final IXtendXpandProject project;
	private XtendXpandSearchResult result;

	/**
	 * Creates a new <code>XtendXpandSearchQuery</code>.
	 * 
	 * @param project
	 *            The project to run this query on.
	 * @param identifier
	 *            The identifier to look for.
	 */
	public XtendXpandSearchQuery(IXtendXpandProject project, String identifier) {
		this.project = project;
		this.identifier = identifier;
	}

	/**
	 * {@inheritDoc}
	 */
	public boolean canRerun() {
		return true;
	}

	/**
	 * {@inheritDoc}
	 */
	public boolean canRunInBackground() {
		return false;
	}

	/**
	 * {@inheritDoc}
	 */
	public String getLabel() {
		return Messages.XtendXpandSearchQuery_Label;
	}

	/**
	 * Returns the label that will be displayed on top of the search result
	 * view.
	 * 
	 * @param matchCount
	 *            The number of search matches.
	 * @return The text for the search result view label.
	 */
	public String getResultLabel(int matchCount) {
		String result = null;
		String searchText = identifier;
		String scope = "project";
		if (matchCount == 1) {
			result = MessageFormat.format("''{0}'' - 1 match in {1}",new Object[]{ searchText, scope});
		} else if (matchCount >= 2) {
			result = MessageFormat.format("''{0}'' - {1} matches in {2}", new Object[]{ searchText, matchCount, scope});
		} else {
			result = MessageFormat.format("''{0}'' - no match found in {1}", new Object[]{ searchText, scope});
		}
		return result;
	}

	/**
	 * {@inheritDoc}
	 */
	public ISearchResult getSearchResult() {
		if (result == null) {
			result = new XtendXpandSearchResult(this);
		}
		return result;
	}

	/**
	 * {@inheritDoc}
	 */
	public IStatus run(IProgressMonitor monitor) throws OperationCanceledException {
		ISearchResult searchResult = getSearchResult();
		if (searchResult instanceof AbstractTextSearchResult) {
			AbstractTextSearchResult result = (AbstractTextSearchResult) searchResult;
			result.removeAll();
		}

		List<SearchMatch> matches = performSearch();
		for (SearchMatch searchMatch : matches) {
			result.addMatch(new Match(searchMatch.getFile(), searchMatch.getOffSet() - 1, searchMatch.getLength()));
		}
		return Status.OK_STATUS;
	}

	/**
	 * @return
	 */
	protected abstract List<SearchMatch> performSearch();

	public String getIdentifier() {
		return identifier;
	}

	/**
	 * Retrurns the project this query is operating on.
	 * 
	 * @return The project this query is operating on.
	 */
	public IXtendXpandProject getProject() {
		return project;
	}

}