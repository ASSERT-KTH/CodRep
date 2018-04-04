putValue(SHORT_DESCRIPTION, "Mark selected messages as Ham");

import java.awt.event.ActionEvent;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.table.selection.TableSelectionChangedEvent;

/**
 * @author fdietz
 * 
 *  
 */
public class MarkMessageAsHamAction
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
	public MarkMessageAsHamAction(FrameMediator frameController) {
		super(frameController, "Mark Message as Ham");

		// tooltip text
		setTooltipText("Mark selected messages as Ham");

		setEnabled(false);
		(
			(
				AbstractMailFrameController) frameController)
					.registerTableSelectionListener(
			this);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
	 */
	public void selectionChanged(SelectionChangedEvent e) {

		if (((TableSelectionChangedEvent) e).getUids().length > 0)
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
				.getTableSelection();

		MainInterface.processor.addOp(new MarkMessageAsHamCommand(r));
	}
}