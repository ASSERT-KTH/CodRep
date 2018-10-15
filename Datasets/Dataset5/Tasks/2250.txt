package org.eclipse.ecf.provider.filetransfer.identity;

package org.eclipse.ecf.provider.internal.filetransfer.identity;

import java.net.URL;

import org.eclipse.ecf.core.identity.BaseID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.filetransfer.identity.IFileID;

public class URLFileID extends BaseID implements IFileID {

	private static final long serialVersionUID = 1274308869502156992L;

	URL fileURL;

	public URLFileID(Namespace namespace, URL url) {
		super(namespace);
		if (url == null)
			throw new NullPointerException("url cannot be null");
		this.fileURL = url;
	}

	protected int namespaceCompareTo(BaseID o) {
		return this.fileURL.toExternalForm().compareTo(
				((URLFileID) o).toExternalForm());
	}

	protected boolean namespaceEquals(BaseID o) {
		return this.fileURL.equals(((URLFileID) o).fileURL);
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

	protected String getFileNameOnly() {
		String path = this.fileURL.getPath();
		String fileName = path.substring(path.lastIndexOf("/") + 1);
		return fileName;
	}

	public String toString() {
		StringBuffer b = new StringBuffer("URLFileID[");
		b.append(toExternalForm());
		b.append("]");
		return b.toString();
	}
}