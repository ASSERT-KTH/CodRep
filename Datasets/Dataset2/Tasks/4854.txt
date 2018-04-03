public class ImportFolderCommandReference extends MailFolderCommandReference {

/*
 * Created on 24.03.2003
 *
 * To change this generated comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.command;

import java.io.File;

import org.columba.mail.folder.AbstractFolder;
import org.columba.mail.folder.mailboximport.AbstractMailboxImporter;


/**
 * @author frd
 *
 * To change this generated comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class ImportFolderCommandReference extends FolderCommandReference {
    File[] sourceFiles;
    AbstractMailboxImporter importer;

    /**
 * @param folder
 */
    public ImportFolderCommandReference(AbstractFolder folder) {
        super(folder);
    }

    /**
 * @param folder
 * @param message
 */
    public ImportFolderCommandReference(AbstractFolder folder,
        File[] sourceFiles, AbstractMailboxImporter importer) {
        super(folder);
        this.sourceFiles = sourceFiles;
        this.importer = importer;
    }

    /**
 * @return AbstractMailboxImporter
 */
    public AbstractMailboxImporter getImporter() {
        return importer;
    }
}