return encoder.encode( new String( bytes ), "US-ASCII" );

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.composer;

import java.io.UnsupportedEncodingException;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Random;

import org.columba.mail.coder.Base64Encoder;
import org.columba.mail.message.MimeHeader;
import org.columba.mail.message.MimePart;

/**
 * @author timo
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public abstract class MimePartRenderer {
	private static final int BOUNDARY_LENGTH = 32;

	public abstract String getRegisterString();

	public abstract String render(MimePart part);

	protected void appendHeader(StringBuffer result, MimeHeader header) {
		result.append("Content-Type:  ");
		result.append(header.getContentType());
		result.append("/");
		result.append(header.getContentSubtype());
		appendParameters(result, header.contentParameter);
		result.append("\n");

		if (header.contentTransferEncoding != null) {
			result.append("Content-Transfer-Encoding: ");
			result.append(header.getContentTransferEncoding());
			result.append("\n");
		}

		if (header.contentDisposition != null) {
			result.append("Content-Disposition: ");
			result.append(header.getContentDisposition());
			appendParameters(result, header.dispositionParameter);
			result.append("\n");
		}

		if (header.contentDescription != null) {
			result.append("Content-Description: ");
			result.append(header.getContentDescription());
			result.append("\n");
		}

		if (header.contentID != null) {
			result.append("Content-ID: ");
			result.append(header.getContentID());
			result.append("\n");
		}
	}

	private void appendParameters(StringBuffer result, Hashtable parameters) {

		Enumeration keys = parameters.keys();
		String key, value;
		
		// Cant use this because of JDK1.3 
		//int lineLength = result.length() - result.lastIndexOf("\n");
		
		// instead :

		int lineLength = 0;
		int actLength = result.length();
		
		while( result.charAt(actLength - lineLength - 1) != '\n' ) {
			lineLength ++;
			if( actLength == lineLength ) break;
		}		


		while (keys.hasMoreElements()) {
			key = (String) keys.nextElement();
			value = (String) parameters.get(key);

			if (lineLength > 75) {
				result.append(";\n ");
				lineLength = 1;
			} else {
				result.append("; ");
			}

			result.append(key);
			result.append("=\"");
			result.append(value);
			result.append("\"");

			lineLength = lineLength + 3 + key.length() + value.length();
		}
	}
	
	protected String createUniqueBoundary() {		
		Random random = new Random();					
		byte[] bytes = new byte[BOUNDARY_LENGTH];
		Base64Encoder encoder = new Base64Encoder();
		
		random.nextBytes(bytes);
		
		try {
			return encoder.encode( new String( bytes ), null );	
		} catch (UnsupportedEncodingException e) {
			// Can never be reached
		}
		
		return null;
	}
	
}