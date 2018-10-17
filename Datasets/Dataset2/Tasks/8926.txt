import org.columba.core.gui.htmlviewer.api.IHTMLViewerPlugin;

package org.columba.core.gui.search;

import java.awt.BorderLayout;
import java.util.Iterator;
import java.util.List;

import javax.swing.JPanel;

import org.columba.core.gui.htmlviewer.HTMLViewerFactory;
import org.columba.core.gui.htmlviewer.IHTMLViewerPlugin;
import org.columba.core.search.api.IResultEvent;
import org.columba.core.search.api.IResultListener;
import org.columba.core.search.api.ISearchCriteria;
import org.columba.core.search.api.ISearchResult;

public class SearchResultView extends JPanel implements IResultListener {

	private IHTMLViewerPlugin viewerPlugin;

	private StringBuffer buf;

	public SearchResultView() {
		super();

		viewerPlugin = HTMLViewerFactory.createHTMLViewer();

		setLayout(new BorderLayout());

		add(viewerPlugin.getContainer(), BorderLayout.CENTER);
	}

	public void resultArrived(IResultEvent event) {
		List<ISearchResult> result = event.getSearchResults();

		buf.append("<p>" + createCriteria(event.getSearchCriteria())
				+ "</p><br>");

		Iterator<ISearchResult> it = result.iterator();
		while (it.hasNext()) {
			ISearchResult r = it.next();
			buf.append("<p>");
			buf.append(createTitle(r));
			buf.append("</p><p>");
			buf.append(getDescription(r));
			buf.append("</p><p><br></p>");
		}

		StringBuffer doc = new StringBuffer();
		startDocument(doc);
		doc.append(buf.toString());
		endDocument(doc);

		viewerPlugin.view(doc.toString());

	}

	private String createCriteria(ISearchCriteria r) {
		return "Search Results for \"<font class=\"italic\">" + r.getTitle() + "</font>\":";
	}

	private String createTitle(ISearchResult r) {
		return "<a href=\"" + r.getLocation().toString() + "\">" + r.getTitle()
				+ "</a>";
	}

	private String getDescription(ISearchResult r) {
		return "<font class=\"quoting\">" + r.getDescription() + "</font>";
	}

	public void clearSearch(IResultEvent event) {
		buf = new StringBuffer();
		viewerPlugin.view("");
	}

	private void startDocument(StringBuffer b) {
		String css = "<style type=\"text/css\">\n"
				+ "a { color: blue; text-decoration: underline }\n"
				+ "font.quoting {color:#949494;} \n font.italic {font-style:italic;color:#000;} \n" + "</style>\n";

		b.append("<HTML><HEAD>" + css + "</HEAD><BODY>");
	}

	private void endDocument(StringBuffer b) {
		b.append("</P></BODY></HTML>");
	}

	public void reset(IResultEvent event) {
		buf = new StringBuffer();
		viewerPlugin.view("");
	}

}