import org.columba.core.resourceloader.ImageLoader;

//The contents of this file are subject to the Mozilla Public License Version 1.1
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
package org.columba.mail.gui.message.viewer;

import java.awt.BorderLayout;
import java.awt.Color;

import javax.swing.BorderFactory;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JPanel;

import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.folder.IMailbox;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.message.MessageController;
import org.columba.mail.gui.message.filter.SecurityStatusEvent;
import org.columba.mail.gui.message.filter.SecurityStatusListener;
import org.columba.mail.parser.text.HtmlParser;
import org.columba.mail.util.MailResourceLoader;

/**
 * IViewer displays security status information.
 * 
 * @author fdietz
 * 
 */
public class EncryptionStatusViewer extends JPanel implements ICustomViewer,
		SecurityStatusListener {

	public static final int DECRYPTION_SUCCESS = 0;

	public static final int DECRYPTION_FAILURE = 1;

	public static final int VERIFICATION_SUCCESS = 2;

	public static final int VERIFICATION_FAILURE = 3;

	public static final int NO_KEY = 4;

	public static final int NOOP = 5;

	protected JLabel icon;

	protected JLabel text;

	protected JPanel left;

	private boolean visible;

	private MessageController mediator;

	public EncryptionStatusViewer(MessageController mediator) {
		super();

		this.mediator = mediator;

		setLayout(new BorderLayout());

		left = new JPanel();
		left.setLayout(new BorderLayout());
		left.setBorder(BorderFactory.createEmptyBorder(0, 5, 5, 5));

		icon = new JLabel();
		left.add(icon, BorderLayout.NORTH);

		add(left, BorderLayout.WEST);
		text = new JLabel();
		add(text, BorderLayout.CENTER);

		setValue(EncryptionStatusViewer.NOOP, "");

		updateUI();

		visible = false;
	}

	public void updateUI() {
		super.updateUI();

		setBackground(Color.white);

		if (icon != null) {
			icon.setBackground(Color.white);
		}

		if (text != null) {
			text.setBackground(Color.white);
		}

		if (left != null) {
			left.setBackground(Color.white);
		}
	}

	private void setValue(int value, String message) {
		switch (value) {
		case EncryptionStatusViewer.DECRYPTION_SUCCESS: {
			icon.setIcon(ImageLoader.getImageIcon("pgp-signature-ok.png"));
			icon.setToolTipText(MailResourceLoader.getString("menu",
					"mainframe", "security_decrypt_success"));
			text.setText(transformToHTML(MailResourceLoader.getString("menu",
					"mainframe", "security_decrypt_success"), message));

			break;
		}

		case EncryptionStatusViewer.DECRYPTION_FAILURE: {
			icon.setIcon(ImageLoader.getImageIcon("pgp-signature-bad.png"));
			icon.setToolTipText(MailResourceLoader.getString("menu",
					"mainframe", "security_encrypt_fail"));
			text.setText(transformToHTML(MailResourceLoader.getString("menu",
					"mainframe", "security_encrypt_fail"), message));

			break;
		}

		case EncryptionStatusViewer.VERIFICATION_SUCCESS: {
			icon.setIcon(ImageLoader.getImageIcon("pgp-signature-ok.png"));
			icon.setToolTipText(MailResourceLoader.getString("menu",
					"mainframe", "security_verify_success"));
			text.setText(transformToHTML(MailResourceLoader.getString("menu",
					"mainframe", "security_verify_success"), message));

			break;
		}

		case EncryptionStatusViewer.VERIFICATION_FAILURE: {
			icon.setIcon(ImageLoader.getImageIcon("pgp-signature-bad.png"));
			icon.setToolTipText(MailResourceLoader.getString("menu",
					"mainframe", "security_verify_fail"));
			text.setText(transformToHTML(MailResourceLoader.getString("menu",
					"mainframe", "security_verify_fail"), message));

			break;
		}

		case EncryptionStatusViewer.NO_KEY: {
			icon.setIcon(ImageLoader.getImageIcon("pgp-signature-nokey.png"));
			icon.setToolTipText(MailResourceLoader.getString("menu",
					"mainframe", "security_verify_nokey"));
			text.setText(transformToHTML(MailResourceLoader.getString("menu",
					"mainframe", "security_verify_nokey"), message));

			break;
		}

		case EncryptionStatusViewer.NOOP: {
			text.setText("");
			icon.setIcon(null);

			break;
		}
		}

		updateUI();
	}

	protected String transformToHTML(String title, String message) {
		// convert special characters
		String html = null;

		if (message != null) {
			html = HtmlParser.substituteSpecialCharacters(message);
		}

		StringBuffer buf = new StringBuffer();

		buf.append("<html><body><p>");
		buf.append("<b>" + title + "</b><br>");
		buf.append(html);
		buf.append("</p></body></html>");

		return buf.toString();
	}

	/**
	 * @see org.columba.mail.gui.message.viewer.IViewer#view(IMailbox,
	 *      java.lang.Object, org.columba.mail.gui.frame.MailFrameMediator)
	 */
	public void view(IMailbox folder, Object uid, MailFrameMediator mediator)
			throws Exception {

	}

	/**
	 * @see org.columba.mail.gui.message.viewer.IViewer#getView()
	 */
	public JComponent getView() {
		return this;
	}

	/**
	 * @see org.columba.mail.gui.message.filter.SecurityStatusListener#statusUpdate(org.columba.mail.gui.message.filter.SecurityStatusEvent)
	 */
	public void statusUpdate(SecurityStatusEvent event) {
		String message = event.getMessage();
		int status = event.getStatus();

		setValue(status, message);

		if (status == NOOP)
			visible = false;
		else
			visible = true;
	}

	/**
	 * @see org.columba.mail.gui.message.viewer.IViewer#isVisible()
	 */
	public boolean isVisible() {
		return visible;
	}

	/**
	 * @see org.columba.mail.gui.message.viewer.IViewer#updateGUI()
	 */
	public void updateGUI() throws Exception {

	}
}