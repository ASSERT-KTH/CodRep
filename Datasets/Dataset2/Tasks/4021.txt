StreamUtils.readCharacterStream(res.getErrorStream()).toString());

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
package org.columba.mail.pgp;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.Vector;

import javax.swing.JOptionPane;

import org.columba.core.io.StreamUtils;
import org.columba.mail.config.SecurityItem;
import org.columba.mail.message.PGPMimePart;
import org.columba.ristretto.composer.MimePartRenderer;
import org.columba.ristretto.composer.MimeTreeRenderer;
import org.columba.ristretto.io.CharSequenceSource;
import org.columba.ristretto.io.SequenceInputStream;
import org.columba.ristretto.io.Source;
import org.columba.ristretto.message.InputStreamMimePart;
import org.columba.ristretto.message.LocalMimePart;
import org.columba.ristretto.message.MimeHeader;
import org.columba.ristretto.message.MimePart;
import org.columba.ristretto.message.StreamableMimePart;
import org.waffel.jscf.JSCFConnection;
import org.waffel.jscf.JSCFResultSet;
import org.waffel.jscf.JSCFStatement;


public class MultipartEncryptedRenderer extends MimePartRenderer {
    private StreamableMimePart controlPart;
    private MimeHeader encryptedHeader;

    public MultipartEncryptedRenderer() {
        MimeHeader controlHeader = new MimeHeader("application", "pgp-encrypted");
        Source controlBody = new CharSequenceSource("Version: 1\r\n");
        controlPart = new LocalMimePart(controlHeader, controlBody);

        encryptedHeader = new MimeHeader("application", "octet-stream");
    }

    /* (non-Javadoc)
 * @see org.columba.ristretto.composer.MimePartRenderer#getRegisterString()
 */
    public String getRegisterString() {
        return "multipart/encrypted";
    }

    /* (non-Javadoc)
 * @see org.columba.ristretto.composer.MimePartRenderer#render(org.columba.ristretto.message.StreamableMimePart)
 */
    public InputStream render(MimePart part) throws Exception {
        Vector streams = new Vector((2 * 2) + 3);

        MimeHeader header = part.getHeader();

        // Create boundary to separate the mime-parts
        String boundary = createUniqueBoundary().toString();
        header.putContentParameter("boundary", boundary);

        byte[] startBoundary = ("\r\n--" + boundary + "\r\n").getBytes();
        byte[] endBoundary = ("\r\n--" + boundary + "--\r\n").getBytes();

        // Add pgp-specific content-parameters
        header.putContentParameter("protocol", "application/pgp-encrypted");

        // Create the header of the multipart
        streams.add(header.getHeader().getInputStream());

        SecurityItem pgpItem = ((PGPMimePart) part).getPgpItem();

        // Add the ControlMimePart 		
        streams.add(new ByteArrayInputStream(startBoundary));
        streams.add(MimeTreeRenderer.getInstance().renderMimePart(controlPart));

        // Add the encrypted MimePart
        streams.add(new ByteArrayInputStream(startBoundary));

        StreamableMimePart encryptedPart;
        encryptedPart = null;

        /*
JSCFDriverManager.registerJSCFDriver(new GPGDriver());
JSCFConnection con = JSCFDriverManager.getConnection("jscf:gpg:"+pgpItem.get("path"));
*/
        JSCFController controller = JSCFController.getInstance();
        JSCFConnection con = controller.getConnection();

        //con.getProperties().put("USERID", pgpItem.get("id"));
        JSCFStatement stmt = con.createStatement();
        JSCFResultSet res = stmt.executeEncrypt(MimeTreeRenderer.getInstance()
                                                                .renderMimePart(part.getChild(
                        0)), pgpItem.get("recipients"));

        if (res.isError()) {
            JOptionPane.showMessageDialog(null,
                StreamUtils.readInString(res.getErrorStream()).toString());
        }

        encryptedPart = new InputStreamMimePart(encryptedHeader,
                res.getResultStream());
        streams.add(MimeTreeRenderer.getInstance().renderMimePart(encryptedPart));

        // Create the closing boundary
        streams.add(new ByteArrayInputStream(endBoundary));

        return new SequenceInputStream(streams);
    }
}