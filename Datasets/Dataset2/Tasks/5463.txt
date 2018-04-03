subject = new String(MailResourceLoader.getString("dialog","composer","composer_no_subject")); //$NON-NLS-1$

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

import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;

import org.columba.mail.gui.composer.util.SubjectDialog;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class SubjectController implements DocumentListener {

	SubjectView view;
	ComposerModel model;

	public SubjectController(ComposerModel model) {
		this.model = model;

		view = new SubjectView(model);
	}

	public void installListener() {
		view.installListener(this);
	}

	public void updateComponents(boolean b) {
		if (b == true) {
			view.setText(model.getHeaderField("Subject"));
		} else {
			model.setHeaderField("Subject", view.getText());
		}
	}

	public boolean checkState() {
		String subject = model.getHeaderField("Subject");

		if (subject.length() == 0) {
			subject = new String(MailResourceLoader.getString("menu","mainframe","composer_no_subject")); //$NON-NLS-1$
			//SubjectDialog dialog = new SubjectDialog(composerInterface.composerFrame);
			SubjectDialog dialog = new SubjectDialog();
			dialog.showDialog(subject);
			if (dialog.success() == true)
				subject = dialog.getSubject();

			model.setHeaderField("Subject", subject);
		}
		
		return true;
	}

	/**************** DocumentListener implementation ***************/

	public void insertUpdate(DocumentEvent e) {

	}
	public void removeUpdate(DocumentEvent e) {

	}
	public void changedUpdate(DocumentEvent e) {

	}

}