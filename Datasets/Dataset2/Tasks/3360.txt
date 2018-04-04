new ConfigFrame(getFrameMediator(), vfolder);

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
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.mail.folder.command;

import java.util.logging.Logger;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.StatusObservableImpl;
import org.columba.core.command.WorkerStatusController;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.filter.FilterCriteria;
import org.columba.mail.filter.FilterRule;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.folder.FolderFactory;
import org.columba.mail.folder.virtual.VirtualFolder;
import org.columba.mail.gui.config.filter.ConfigFrame;
import org.columba.mail.main.MailInterface;
import org.columba.ristretto.message.Header;


/**
 * This class is used to create a virtual folder based on the currently
 * selected message (if multiple selected, the first one in the selection array
 * is used) - either using Subject, To or From.
 *
 * @author Karl Peder Olesen (karlpeder), 20030621
 */
public class CreateVFolderOnMessageCommand extends FolderCommand {

    /** JDK 1.4+ logging framework logger, used for logging. */
    private static final Logger LOG = Logger.getLogger("org.columba.mail.folder.command");

    /** Used for creating a virtual folder based on Subject */
    public static final String VFOLDER_ON_SUBJECT = "Subject";

    /** Used for creating a virtual folder based on From */
    public static final String VFOLDER_ON_FROM = "From";

    /** Used for creating a virtual folder based on To */
    public static final String VFOLDER_ON_TO = "To";

    /** Type of virtual folder to create (Subject/From/To) */
    private String vfolderType;

    /** Parent for the virtual folder */
    private MessageFolder parentFolder = null;

    /** Virtual folder created created */
    private VirtualFolder vfolder = null;

    /**
     * Constructor for CreateVFolderOnMessageCommand. Calls super constructor
     * and saves flag for which kind of virtual folder to create. Default for
     * filter type is FILTER_ON_SUBJECT.
     *
     * @param frameMediator
     * @param references
     * @param vfolderType
     *            Which type of filter to create. Used defined constants
     */
    public CreateVFolderOnMessageCommand(FrameMediator frameController,
        DefaultCommandReference[] references, String vfolderType) {
        super(frameController, references);
        this.vfolderType = vfolderType;
    }

    /**
     * Displays search dialog for user modifications after creation of the
     * virtual folder in execute. Also refreshes the tree view.
     *
     * @see org.columba.core.command.Command#updateGUI()
     */
    public void updateGUI() throws Exception {
        MailInterface.treeModel.nodeStructureChanged(parentFolder);

        if (vfolder != null) {
            //vfolder.showFilterDialog((AbstractMailFrameController) getFrameMediator());
            new ConfigFrame(getFrameMediator().getView().getFrame(), vfolder);
        }
    }

    /**
     * This method generates a virtual folder based on Subject, From or To
     * (depending on parameter transferred to constructor) of the currently
     * selected message.
     *
     * @param worker
     * @see org.columba.core.command.Command#execute(Worker)
     */
    public void execute(WorkerStatusController worker)
        throws Exception {
        // get references to selected folder and message
        FolderCommandReference[] r = (FolderCommandReference[]) getReferences();
        Object[] uids = r[0].getUids(); // uid for messages to save

        if (uids.length == 0) {
            LOG.fine(
                "No virtual folder created since no message was selected");

            return; // no message selected.
        }

        Object uid = uids[0];
        parentFolder = (MessageFolder) r[0].getFolder();

        //register for status events
        ((StatusObservableImpl) parentFolder.getObservable()).setWorker(worker);

        // get value of Subject, From or To header
        Header header = parentFolder.getHeaderFields(uid,
                new String[] {"Subject", "From", "To"});
        String headerValue = (String) header.get(vfolderType);

        if (headerValue == null) {
            LOG.warning("Error getting " + vfolderType
                    + " header. No virtual folder created");

            return;
        }

        // create virtual folder (is attached to parentFolder)
        String name = vfolderType + " contains [" + headerValue + "]";
        vfolder = createVirtualFolder(name, vfolderType, headerValue,
                parentFolder);
    }

    /**
     * Private utility for creating a virtual folder on a given headerfield.
     * The criteria used is "contains".
     *
     * @param folderName
     *            Name of virtual folder
     * @param headerField
     *            The header field to base virtual folder on
     * @param pattern
     *            The pattern to use in the virtual folder
     * @param parent
     *            Parent folder
     * @return The filter created
     */
    public VirtualFolder createVirtualFolder(String folderName,
        String headerField, String pattern, MessageFolder parent) {
        // create virtual folder
        VirtualFolder vfolder;

        try {
            vfolder = (VirtualFolder) FolderFactory.getInstance().createChild(parent,
                    folderName, "VirtualFolder");
        } catch (Exception e) {
            LOG.warning("Error creating new virtual folder: "
                    + e.getMessage());

            return null;
        }

        // set properties for virtual folder
        int parentUid = 101; // default is inbox if parent is null

        if (parent != null) {
            parentUid = parent.getUid();
        }

        vfolder.getConfiguration().set("property", "source_uid", parentUid);
        vfolder.getConfiguration().set("property", "include_subfolders", false);

        // define filter rule
        FilterRule rule = vfolder.getFilter().getFilterRule();
        rule.setCondition("matchall");
        rule.removeAll();
        rule.addEmptyCriteria();

        // define criteria
        FilterCriteria c = rule.get(0);
        c.setCriteria("contains");
        c.setHeaderItem(headerField);
        c.setType(headerField);
        c.setPattern(pattern);

        return vfolder;
    }
}