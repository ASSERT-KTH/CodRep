((MailFrameMediator) frameMediator).registerTreeSelectionListener(

import java.awt.event.ActionEvent;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.tree.selection.TreeSelectionChangedEvent;

/**
 * @author fdietz
 * 
 *  
 */
public class AnalyzeFolderAction
	extends FrameAction
	implements SelectionListener {

	/**
	 * @param frameMediator
	 * @param name
	 * @param longDescription
	 * @param actionCommand
	 * @param small_icon
	 * @param big_icon
	 * @param mnemonic
	 * @param keyStroke
	 */
	public AnalyzeFolderAction(FrameMediator frameMediator) {
		super(frameMediator, "Analyze Folder");

		// tooltip text
		putValue(SHORT_DESCRIPTION, "Analyze all messages of selected Folder");

		setEnabled(false);

		((MailFrameMediator) frameMediator).registerTableSelectionListener(
			this);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
	 */
	public void selectionChanged(SelectionChangedEvent e) {

		if (((TreeSelectionChangedEvent) e).getSelected().length > 0)
			setEnabled(true);
		else
			setEnabled(false);

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		FolderCommandReference[] r =
			((AbstractMailFrameController) getFrameMediator())
				.getTreeSelection();

		MainInterface.processor.addOp(new AnalyzeFolderCommand(r));
	}
}