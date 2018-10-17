Association association = new AssociationService().getMimeTypeAssociation("text/plain");

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
//(the "License"); you may not use this file except in compliance with the
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.mail.gui.composer.util;

import java.awt.Font;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

import javax.swing.JOptionPane;

import org.columba.core.gui.util.FontProperties;
import org.columba.core.io.TempFileStore;
import org.columba.mail.gui.composer.AbstractEditorController;
import org.columba.mail.util.MailResourceLoader;
import org.columba.ristretto.message.MimeHeader;
import org.jdesktop.jdic.filetypes.Action;
import org.jdesktop.jdic.filetypes.Association;
import org.jdesktop.jdic.filetypes.AssociationService;

public class ExternalEditor {
	String Cmd;

	public ExternalEditor() {
	}

	// END public ExternalEditor()
	public ExternalEditor(String EditorCommand) {
	}

	// END public ExternalEditor(String EditorCommand)
	public boolean startExternalEditor(AbstractEditorController EditCtrl) throws IOException {
		/*
		 * *20030906, karlpeder* Method signature changed to take an
		 * AbstractEditorController (instead of an TextEditorView) as parameter
		 * since the view is no longer directly available
		 */
		MimeHeader myHeader = new MimeHeader("text", "plain");
		File tmpFile = TempFileStore.createTempFileWithSuffix("extern_edit");
		FileWriter FO;
		FileReader FI;

		try {
			FO = new FileWriter(tmpFile);
		} catch (java.io.IOException ex) {
			JOptionPane.showMessageDialog(null,
					"Error: Cannot write to temp file needed "
							+ "for external editor.");

			return false;
		}

		try {
			//String M = EditView.getText();
			String M = EditCtrl.getViewText();

			if (M != null) {
				FO.write(M);
			}

			FO.close();
		} catch (java.io.IOException ex) {
			JOptionPane.showMessageDialog(null,
					"Error: Cannot write to temp file needed "
							+ "for external editor:\n" + ex.getMessage());

			return false;
		}

		//Font OldFont = EditView.getFont();
		Font OldFont = EditCtrl.getViewFont();

		/*
		 * // Why doesn't this work??? EditView.setFont( new
		 * Font(Config.getOptionsConfig().getThemeItem().getTextFontName(),
		 * Font.BOLD, 30));
		 */
		Font font = FontProperties.getTextFont();
		font = font.deriveFont(30);

		//EditView.setFont(font);
		EditCtrl.setViewFont(font);

		//EditView.setText(
		EditCtrl.setViewText(MailResourceLoader.getString("menu", "composer",
				"extern_editor_using_msg"));

		// execute application, enabling blocking
		Association association = new AssociationService().getFileExtensionAssociation("txt");
		Action action = association.getActionByVerb("edit");
		
		
		Process child = Runtime.getRuntime().exec(
				action.getCommand() + " " + tmpFile.toString());

		if (child == null) {
			return false;
		}

		try {
			// Wait for external editor to quit
			child.waitFor();

		} catch (InterruptedException ex) {
			JOptionPane.showMessageDialog(null,
					"Error: External editor exited " + "abnormally.");

			return false;
		}

		//EditView.setFont(OldFont);
		EditCtrl.setViewFont(OldFont);

		try {
			FI = new FileReader(tmpFile);
		} catch (java.io.FileNotFoundException ex) {
			JOptionPane.showMessageDialog(null,
					"Error: Cannot read from temp file used "
							+ "by external editor.");

			return false;
		}

		//      int i = FI.available();
		char[] buf = new char[1000];
		int i;
		String message = "";

		try {
			while ((i = FI.read(buf)) >= 0) {
				//System.out.println( "*>"+String.copyValueOf(buf)+"<*");
				message += new String(buf, 0, i);

				//System.out.println( "-->"+Message+"<--");
			}

			FI.close();
		} catch (java.io.IOException ex) {
			JOptionPane.showMessageDialog(null,
					"Error: Cannot read from temp file used "
							+ "by external editor.");

			return false;
		}

		//System.out.println( "++>"+Message+"<++");
		//System.out.println( Message.length());
		//EditView.setText(message);
		EditCtrl.setViewText(message);

		return true;
	}

	// END public boolean startExternalEditor()
}

// END public class ExternalEditor