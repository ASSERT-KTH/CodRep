FolderCommandReference r = ((AbstractMailFrameController) getFrameMediator()).getTableSelection();

import org.columba.core.action.AbstractColumbaAction;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.main.MainInterface;

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.table.selection.TableSelectionChangedEvent;

import java.awt.event.ActionEvent;


/**
 * @author fdietz
 *
 * command:
 *
 * spamassassin -a --remove-addr-from-whitelist="address"
 *
 * command description:
 *
 * -a, --auto-whitelist, --whitelist
 *
 * Use auto-whitelists. Auto-whitelists track the long-term average score for
 * each sender and then shift the score of new messages toward that long-term
 * average. This can increase or decrease the score for messages, depending on
 * the long-term behavior of the particular correspondent. See the README file
 * for more details.
 *
 * --remove-addr-from-whitelist
 *
 * Remove the named email address from the automatic whitelist. Note that you
 * must be running spamassassin or spamd with the -a switch.
 *
 */
public class RemoveAddressFromWhiteListAction extends AbstractColumbaAction
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
    public RemoveAddressFromWhiteListAction(FrameMediator frameMediator) {
        super(frameMediator, "Remove Address from Whitelist");

        // tooltip text
        putValue(SHORT_DESCRIPTION, "Remove Address from Whitelist");

        setEnabled(false);

        ((MailFrameMediator) frameMediator).registerTableSelectionListener(this);
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
     */
    public void selectionChanged(SelectionChangedEvent e) {
        if (((TableSelectionChangedEvent) e).getUids().length > 0) {
            setEnabled(true);
        } else {
            setEnabled(false);
        }
    }

    /*
     * (non-Javadoc)
     *
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        FolderCommandReference[] r = ((AbstractMailFrameController) getFrameMediator()).getTableSelection();

        MainInterface.processor.addOp(new RemoveAddressFromWhiteListCommand(r));
    }
}