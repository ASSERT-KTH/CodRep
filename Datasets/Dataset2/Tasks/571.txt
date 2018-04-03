super(MailResourceLoader.getString("dialog","composer","composer_no_subject")); //$NON-NLS-1$

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

package org.columba.mail.gui.composer;

import javax.swing.JTextField;

import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class SubjectView extends JTextField {
	
	ComposerModel model;
	
	public SubjectView( ComposerModel model )
	{
		super(MailResourceLoader.getString("action","mainframe","composer_no_subject")); //$NON-NLS-1$
		
		this.model = model;
		
		
	}
	
	public void installListener( SubjectController controller )
	{
		getDocument().addDocumentListener(controller);
	}
	
	
	

}