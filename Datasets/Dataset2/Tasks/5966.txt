return "subject_contains";

/**
 * 
 */
package org.columba.mail.search;

import org.columba.core.filter.FilterCriteria;
import org.columba.core.search.SearchCriteria;
import org.columba.core.search.api.ISearchCriteria;
import org.columba.core.search.api.ISearchProvider;
import org.columba.mail.filter.MailFilterFactory;

/**
 * @author frd
 * 
 */
public class SubjectContainsSearchProvider extends AbstractMailSearchProvider implements
		ISearchProvider {

	public SubjectContainsSearchProvider() {
		super();
	}

	/**
	 * @see org.columba.core.search.api.ISearchProvider#getName()
	 */
	public String getName() {
		return "Subject_Contains";
	}

	/**
	 * @see org.columba.core.search.api.ISearchProvider#getNamespace()
	 */
	public String getNamespace() {
		return "org.columba.mail";
	}

	/**
	 * @see org.columba.core.search.api.ISearchProvider#getCriteria(java.lang.String)
	 */
	public ISearchCriteria getCriteria(String searchTerm) {
		return new SearchCriteria("Subject contains " + searchTerm,
				"Subject contains " + searchTerm);
	}

	@Override
	protected FilterCriteria createFilterCriteria(String searchTerm) {
		FilterCriteria criteria = MailFilterFactory
				.createSubjectContains(searchTerm);
		return criteria;
	}

}