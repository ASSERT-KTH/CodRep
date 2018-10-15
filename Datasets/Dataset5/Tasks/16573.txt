Assert.isNotNull(url, Messages.FileTransferID_Exception_Url_Not_Null);

package org.eclipse.ecf.provider.filetransfer.identity;

import java.net.URL;

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.identity.BaseID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.filetransfer.identity.IFileID;
import org.eclipse.ecf.internal.provider.filetransfer.Messages;

public class FileTransferID extends BaseID implements IFileID {

	private static final long serialVersionUID = 1274308869502156992L;

	URL fileURL;

	public FileTransferID(Namespace namespace, URL url) {
		super(namespace);
		Assert.isNotNull(url, Messages.FileTransferID_Exception_Url_Not_Null); //$NON-NLS-1$
		this.fileURL = url;
	}

	protected int namespaceCompareTo(BaseID o) {
		return this.fileURL.toExternalForm().compareTo(
				((FileTransferID) o).toExternalForm());
	}

	protected boolean namespaceEquals(BaseID o) {
		return this.fileURL.equals(((FileTransferID) o).fileURL);
	}

	protected String namespaceGetName() {
		return this.fileURL.toExternalForm();
	}

	protected int namespaceHashCode() {
		return this.fileURL.hashCode();
	}

	public String getFilename() {
		return getFileNameOnly();
	}

	public URL getURL() {
		return this.fileURL;
	}

	protected String getFileNameOnly() {
		String path = this.fileURL.getPath();
		return path.substring(path.lastIndexOf("/") + 1); //$NON-NLS-1$;
	}

	public String toString() {
		StringBuffer b = new StringBuffer("FileTransferID["); //$NON-NLS-1$
		b.append(toExternalForm());
		b.append("]"); //$NON-NLS-1$
		return b.toString();
	}
}