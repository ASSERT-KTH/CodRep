Message message = new Message();

package org.columba.mail.folder.command;

import java.awt.Color;
import java.awt.Font;
import java.lang.reflect.Array;
import java.text.DateFormat;
import java.util.Date;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.core.print.cCmUnit;
import org.columba.core.print.cDocument;
import org.columba.core.print.cHGroup;
import org.columba.core.print.cLine;
import org.columba.core.print.cParagraph;
import org.columba.core.print.cPrintObject;
import org.columba.core.print.cPrintVariable;
import org.columba.core.print.cVGroup;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.MailConfig;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.table.util.MessageNode;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.Message;
import org.columba.mail.message.MimePart;
import org.columba.mail.message.MimePartTree;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class PrintMessageCommand extends FolderCommand {

	private cPrintObject mailHeader;
	private cPrintObject mailFooter;
	private DateFormat mailDateFormat;
	private String[] headerKeys = { "from", "to","date", "subject" };
	
	/**
	 * Constructor for PrintMessageCommdn.
	 * @param frameController
	 * @param references
	 */
	public PrintMessageCommand(
		FrameController frameController,
		DefaultCommandReference[] references) {
		super(frameController, references);
		
		
		// Header

		cParagraph columbaParagraph = new cParagraph();
		columbaParagraph.setText( "The Columba Project");
		columbaParagraph.setColor( Color.lightGray );
		columbaParagraph.setFontStyle( Font.BOLD );

		cParagraph link = new cParagraph();
		link.setText(" - http://sourceforge.columba.net");
		link.setTextAlignment( cParagraph.LEFT );
		link.setLeftMargin( columbaParagraph.getSize(new cCmUnit(100)).getWidth() );
		link.setColor( Color.lightGray );

		cPrintVariable date = new cPrintVariable();
		date.setCodeString( "%DATE_TODAY%" );
		date.setTextAlignment( cParagraph.RIGHT );
		date.setColor( Color.lightGray );


		cHGroup headerText = new cHGroup();
		headerText.add( columbaParagraph );
		headerText.add( link );
		headerText.add( date );


		cLine headerLine = new cLine();

		headerLine.setThickness( 1 );
		headerLine.setColor( Color.lightGray );
		headerLine.setTopMargin( new cCmUnit( 0.1 ) );

		cVGroup header = new cVGroup();
		header.add( headerText );
		header.add( headerLine );
		header.setBottomMargin( new cCmUnit( 0.5 ) );

		mailHeader = header;

		// Footer

		cPrintVariable footer = new cPrintVariable();
		footer.setTextAlignment( cParagraph.CENTER );
		footer.setCodeString( "%PAGE_NR% / %PAGE_COUNT%" );
		footer.setTopMargin( new cCmUnit( 0.5 ) );
		footer.setColor( Color.lightGray );

		mailFooter = footer;

		// DateFormat

		mailDateFormat = DateFormat.getDateTimeInstance(DateFormat.LONG, DateFormat.MEDIUM);
	}

	public cPrintObject getMailHeader() {
		return mailHeader;
	}

	public cPrintObject getMailFooter() {
		return mailFooter;
	}

	public String[] getHeaderKeys() {
		return headerKeys;
	}

	public DateFormat getMailDateFormat() {
		return mailDateFormat;
	}
	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updatedGUI() throws Exception {
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		
		MailFrameController mailFrameController =
			(MailFrameController) frameController;

		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

		Object[] uids = r[0].getUids();

		Folder srcFolder = (Folder) r[0].getFolder();

		for (int j = 0; j < uids.length; j++) {
			Object uid = uids[j];
			//ColumbaLogger.log.debug("copying UID=" + uid);

			Message message = (Message) srcFolder.getMessage(uid, worker);

			ColumbaHeader header = srcFolder.getMessageHeader(uid, worker);

			MimePartTree mimePartTree = srcFolder.getMimePartTree(uid, worker);

			boolean viewhtml =
				MailConfig
					.getMainFrameOptionsConfig()
					.getWindowItem()
					.getHtmlViewer();

			// Which Bodypart shall be shown? (html/plain)
			MimePart bodyPart = null;
			if (viewhtml)
				bodyPart = mimePartTree.getFirstTextPart("html");
			else
				bodyPart = mimePartTree.getFirstTextPart("plain");

			if (bodyPart == null) {
				bodyPart = new MimePart();
				bodyPart.setBody(new String("<No Message-Text>"));
			} else
				bodyPart =
					srcFolder.getMimePart(uid, bodyPart.getAddress(), worker);

			cDocument messageDoc = new cDocument();

			messageDoc.setHeader(getMailHeader());
			messageDoc.setFooter(getMailFooter());

			String[] headerKeys = getHeaderKeys();
			cParagraph hKey, hValue;
			cHGroup hLine;
			Object value;

			for (int i = 0; i < Array.getLength(headerKeys); i++) {
				hKey = new cParagraph();
				hKey.setText(
					MailResourceLoader.getString("header", headerKeys[i]));
				hKey.setFontStyle(Font.BOLD);

				hValue = new cParagraph();
				if (headerKeys[i].equals("date")) {
					value = header.get("columba.date");
				} else {
					value = header.get(headerKeys[i]);
				}

				if (value instanceof Date) {
					hValue.setText(
						getMailDateFormat().format((Date) value));
				} else {
					hValue.setText((String) value);
				}
				hValue.setLeftMargin(new cCmUnit(3.0));

				hLine = new cHGroup();
				hLine.add(hKey);
				hLine.add(hValue);

				messageDoc.appendPrintObject(hLine);

				cParagraph body = new cParagraph();
				body.setTopMargin(new cCmUnit(1.0));

				messageDoc.appendPrintObject(body);

				messageDoc.print();
			}
		}
		
	}

}