package org.eclipse.ecf.provider.filetransfer.identity;

package org.eclipse.ecf.internal.provider.filetransfer.identity;

import java.net.URL;

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.identity.BaseID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.filetransfer.identity.IFileID;

public class FileTransferID extends BaseID implements IFileID {

	private static final long serialVersionUID = 1274308869502156992L;

	URL fileURL;

	public FileTransferID(Namespace namespace, URL url) {
		super(namespace);
		Assert.isNotNull(url,"url cannot be null");
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
		String fileName = path.substring(path.lastIndexOf("/") + 1);
		return fileName;
	}

	public String toString() {
		StringBuffer b = new StringBuffer("FileTransferID[");
		b.append(toExternalForm());
		b.append("]");
		return b.toString();
	}
}