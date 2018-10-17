int rgb = filterAction.getIntegerWithDefault("rgb", Color.black.getRGB());

package org.columba.mail.filter.plugins;

import java.awt.Color;

import org.columba.core.command.Command;
import org.columba.core.filter.AbstractFilterAction;
import org.columba.core.filter.FilterAction;
import org.columba.core.folder.IFolder;
import org.columba.mail.command.MailFolderCommandReference;
import org.columba.mail.folder.command.ColorMessageCommand;


/**
 * This Filter Action colors a message with a specified color. The action
 * retrieves the integer attribute "<b>rgb</b>" from the filter action as
 * the color to color the message with. In order to keep the memory consumtion
 * up, it creates the <code>Color</code> object by using the <code>ColorFactory</code>.
 * The message is colored by setting the "<b>columba.color</b>" header.
 *
 * @author redsolo
 */
public class ColorMessageFilterAction extends AbstractFilterAction {
    /** {@inheritDoc} */
    public Command getCommand(FilterAction filterAction, IFolder srcFolder,
        Object[] uids) throws Exception {
        int rgb = filterAction.getInteger("rgb", Color.black.getRGB());

        // create reference
        MailFolderCommandReference r = new MailFolderCommandReference(srcFolder, uids);
        r.setColorValue(rgb);

        // create command
        return new ColorMessageCommand(r);
    }
}