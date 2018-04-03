else return "application/octet-stream";

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

import java.io.IOException;
import java.io.InputStream;
import java.util.Hashtable;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.columba.core.io.DiskIO;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

public class MimeTypeLookup
{

	private Hashtable extTable;
	

	public MimeTypeLookup ()
    {
		extTable = new Hashtable();
		loadExtensionList();
	}

	private boolean loadExtensionList ()
    {
		InputStream extList;

		// Get InputStream of ext2mime
	    try	{
	    extList = DiskIO.getResourceStream( "org/columba/mail/composer/ext2mime.xml" );
		}
		catch (IOException e)
			{
			System.err.println( e );
			return false;
			}

		// Parse InputStream

        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		Document document;

        try
        {
            DocumentBuilder builder = factory.newDocumentBuilder();

            builder.setErrorHandler
                (
                    new org.xml.sax.ErrorHandler()
                        {

                            public void fatalError(SAXParseException exception)
                                throws SAXException
                            {
                            }


                            public void error (SAXParseException e)
                                throws SAXParseException
                            {
                                throw e;
                            }


                            public void warning (SAXParseException err)
                                throws SAXParseException
                            {
                                System.out.println ("** Warning"
                                                    + ", line " + err.getLineNumber ()
                                                    + ", uri " + err.getSystemId ());
                                System.out.println("   " + err.getMessage ());
                            }
                        }
                    );

            document = builder.parse( extList );

            // Write Extensions in Hashtable for faster lookup

			Node mimeNode, extNode;
			NodeList rootNodes = document.getFirstChild().getChildNodes();
			NodeList mimeNodes;
			String mimeTypeName;
			String ext;

			for( int i=0; i<rootNodes.getLength(); i++ ) {
				mimeTypeName = null;
				mimeNode = rootNodes.item(i);

				if( mimeNode.getNodeName().equals("mime-type") ) {
					mimeNodes = mimeNode.getChildNodes();

					// Get MimeType name first

					for( int j=0; j<mimeNodes.getLength(); j++ ) {
						if( mimeNodes.item(j).getNodeName().equals("name") ) {
							mimeTypeName = mimeNodes.item(j).getFirstChild().toString();
							break;
						}
					}

					if( mimeTypeName == null ) break;

					// Put extensions in extTable

					for( int j=0; j<mimeNodes.getLength(); j++ ) {
						if( mimeNodes.item(j).getNodeName().equals("ext") ) {
							ext = mimeNodes.item(j).getFirstChild().toString();
							extTable.put( ext, mimeTypeName );
						}
					}
				}
			}

        }

	catch (SAXParseException spe)
        {
            System.out.println ("\n** Parsing error"
                                + ", line " + spe.getLineNumber ()
                                + ", uri " + spe.getSystemId ());
            System.out.println("   " + spe.getMessage() );

            Exception  x = spe;
            if (spe.getException() != null)
                x = spe.getException();
            x.printStackTrace();

        } catch (SAXException sxe)
        {
            Exception  x = sxe;
            if (sxe.getException() != null)
		    x = sxe.getException();
            x.printStackTrace();

        } catch (ParserConfigurationException pce)
        {
                pce.printStackTrace();
        } catch (IOException ioe)
        {
            ioe.printStackTrace();
        }


		return true;
	}

	public String getMimeType( String ext )
    {
    	if ( ext == null ) return "application/octet-stream";
    	
	   if( extTable.containsKey( ext ) )
           return (String) extTable.get( ext );

	   else return new String( "application/octet-stream" );
    }

}