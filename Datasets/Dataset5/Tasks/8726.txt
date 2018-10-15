package org.eclipse.ecf.internal.example.collab.ui.hyperlink;

package org.eclipse.ecf.example.collab.ui.hyperlink;

import java.net.URI;

import org.eclipse.ecf.ui.hyperlink.AbstractURLHyperlinkDetector;
import org.eclipse.jface.text.IRegion;
import org.eclipse.jface.text.hyperlink.IHyperlink;

public class ECFGenericHyperlinkDetector extends AbstractURLHyperlinkDetector {

	public static final String ECFGENERIC_PROTOCOL = "ecftcp"; //$NON-NLS-1$
	
	public ECFGenericHyperlinkDetector() {
		setProtocols(new String [] { ECFGENERIC_PROTOCOL });
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.ui.hyperlink.AbstractURLHyperlinkDetector#createHyperLinksForURI(org.eclipse.jface.text.IRegion, java.net.URI)
	 */
	protected IHyperlink[] createHyperLinksForURI(IRegion region, URI uri) {
		return new IHyperlink[] { new ECFGenericHyperlink(region, uri) };
	}	

}