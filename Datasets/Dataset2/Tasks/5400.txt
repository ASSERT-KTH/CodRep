.equals("org.columba.mail.composer.MimePartRenderer")) {

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.composer;

import java.lang.reflect.Array;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.Hashtable;

import org.columba.core.io.DiskIO;
import org.columba.mail.message.MimeHeader;
import org.columba.mail.message.MimePart;
import org.columba.mail.message.MimePartTree;

/**
 * @author timo
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class MimeTreeRenderer {
	
	private static final String rendererPath = "org.columba.mail.composer.mimepartrenderers.";
	
	private static final String[] renderers = {
		"MultipartRenderer", "MultipartSignedRenderer" };
	
	private static MimeTreeRenderer myInstance;
	
	private Hashtable rendererTable;
	private MimePartRenderer defaultRenderer;
	
	protected MimeTreeRenderer() {
		rendererTable = new Hashtable();
		loadAllRenderer();
		
		defaultRenderer = new DefaultMimePartRenderer();
	}
	
	public static MimeTreeRenderer getInstance() {
		
		if( myInstance == null )
			myInstance = new MimeTreeRenderer();
		
		return myInstance;	
	}
	
	public String render( MimePartTree tree ) {
		return renderMimePart( tree.getRootMimeNode() );
	}
	
	public String renderMimePart( MimePart part ) {		
		MimePartRenderer renderer = getRenderer( part.getHeader() );
		
		return renderer.render(part);	
	}
	
	private MimePartRenderer getRenderer( MimeHeader input ) {
		// If no ContentType specified return StandardParser
		if (input.contentType == null)
			return defaultRenderer;

		MimePartRenderer renderer;

		// First try to find renderer for "type/subtype"

		renderer =
			(MimePartRenderer) rendererTable.get(
				input.contentType + "/" + input.contentSubtype);
		if (renderer != null) {
			return renderer;
		}

		// Next try to find renderer for "type"

		renderer = (MimePartRenderer) rendererTable.get(input.contentType);
		if (renderer != null) {
			return renderer;
		}

		// Nothing found -> return Standardrenderer
		return defaultRenderer;
		
	}

	private void loadAllRenderer() {
		ClassLoader loader = ClassLoader.getSystemClassLoader();
		Class actClass = null;

		try {
			for (int i = 0; i < Array.getLength(renderers); i++) {
				actClass = loader.loadClass(rendererPath + renderers[i]);

				if (actClass
					.getSuperclass()
					.getName()
					.equals("org.columba.modules.mail.composer.MimePartRenderer")) {

					MimePartRenderer renderer =
						(MimePartRenderer) actClass.newInstance();
							
					rendererTable.put( renderer.getRegisterString(), renderer);
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

}