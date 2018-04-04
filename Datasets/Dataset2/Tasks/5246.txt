return new SearchCriteria("test: "+searchTerm, "test description", null);

package org.columba.core.search;

import java.net.MalformedURLException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.List;
import java.util.Vector;

import org.columba.core.search.api.ISearchCriteria;
import org.columba.core.search.api.ISearchProvider;
import org.columba.core.search.api.ISearchResult;


public class ExampleSearchProvider implements ISearchProvider {

	private int count = -1;
	
	public ExampleSearchProvider() {
		super();
	}

	public ISearchCriteria getCriteria(String searchTerm) {
		return new SearchCriteria("test: "+searchTerm, "test description");
	}

	/**
	 * @see org.columba.core.search.api.ISearchProvider#query(java.lang.String, int, int)
	 */
	public List<ISearchResult> query(String searchTerm, int startIndex, int resultCount) {
		
		URI url=null;
		try {
			url = new URI("columba://org.columba.core.example/test");
		} catch (URISyntaxException e) {
			e.printStackTrace();
		}
		
		
		List<ISearchResult> result = new Vector<ISearchResult>();
		result.add(new SearchResult("item1", "item1 description", url));
		result.add(new SearchResult("item2", "item2 description", url));
		result.add(new SearchResult("item3", "item3 description", url));
		
		count = result.size();
		
		return result;
	}

	public String getName() {
		return "example";
	}

	public String getNamespace() {
		return "org.columba.core.example";
	}

	public int getTotalResultCount() {
		return count;
	}
}