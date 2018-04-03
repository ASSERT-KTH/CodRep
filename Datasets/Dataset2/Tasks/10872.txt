Object[] uids = inboxFolder.getUids();

/*
 * Created on 06.04.2003
 *
 * To change the template for this generated file go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.messageframe;

import org.columba.core.config.ViewItem;
import org.columba.core.gui.frame.AbstractFrameView;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.MailConfig;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.attachment.AttachmentSelectionHandler;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.message.command.ViewMessageCommand;

/**
 * @author frd
 *
 * To change the template for this generated type comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class MessageFrameController extends AbstractMailFrameController {

	FolderCommandReference[] treeReference;
	FolderCommandReference[] tableReference;

	FixedTableSelectionHandler tableSelectionHandler;
	
	/**
	 * @param viewItem
	 */
	public MessageFrameController() {
		super(
			"MessageFrame",
			new ViewItem(
				MailConfig.get("options").getElement(
					"/options/gui/messageframe/view")));

		getView().loadWindowPosition();

		getView().setVisible(true);
	}

	protected void init() {
		super.init();

		tableSelectionHandler = new FixedTableSelectionHandler(tableReference);
		getSelectionManager().addSelectionHandler(tableSelectionHandler);

		getSelectionManager().addSelectionHandler(
			new AttachmentSelectionHandler(attachmentController.getView()));
	}

	public void selectInbox() {
		Folder inboxFolder = (Folder) MainInterface.treeModel.getFolder(101);
		try {

			Object[] uids = inboxFolder.getUids(null);
			if (uids.length > 0) {
				Object uid = uids[0];

				Object[] newUids = new Object[1];
				newUids[0] = uid;

				FolderCommandReference[] r = new FolderCommandReference[1];
				r[0] = new FolderCommandReference(inboxFolder, newUids);

				// set tree and table references
				treeReference = new FolderCommandReference[1];
				treeReference[0] = new FolderCommandReference(inboxFolder);

				tableReference = new FolderCommandReference[1];
				tableReference[0] =
					new FolderCommandReference(inboxFolder, newUids);

				// FIXME
				/*
				getSelectionManager().getHandler("mail.table").setSelection(r);
				*/

				MainInterface.processor.addOp(new ViewMessageCommand(this, r));
			}
		} catch (Exception ex) {
			ex.printStackTrace();
		}

	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.frame.AbstractFrameController#createView()
	 */
	public AbstractFrameView createView() {
		MessageFrameView view = new MessageFrameView(this);

		/*
		view.setFolderInfoPanel(folderInfoPanel);
		*/

		view.init(messageController.getView(), statusBar);

		view.pack();

		view.setVisible(true);

		return view;
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.frame.AbstractFrameController#close()
	 */
	public void close() {
		view.saveWindowPosition();

		view.setVisible(false);
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.frame.AbstractFrameController#saveAndClose()
	 */
	public void saveAndClose() {

		super.saveAndClose();
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.frame.AbstractFrameController#initInternActions()
	 */
	protected void initInternActions() {

	}

	/* (non-Javadoc)
	 * @see org.columba.mail.gui.frame.MailFrameInterface#getTableSelection()
	 */
	public FolderCommandReference[] getTableSelection() {
		return tableReference;
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.gui.frame.MailFrameInterface#getTreeSelection()
	 */
	public FolderCommandReference[] getTreeSelection() {
		return treeReference;
	}

	/**
	 * @param references
	 */
	public void setTreeSelection(FolderCommandReference[] references) {
		treeReference = references;
	}

	/**
	 * @param references
	 */
	public void setTableSelection(FolderCommandReference[] references) {
		tableReference = references;
		
		tableSelectionHandler.setSelection(tableReference);
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.gui.frame.AbstractMailFrameController#hasTable()
	 */
	public boolean hasTable() {
		return false;
	}

}