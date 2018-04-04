return new String( input.getBytes(charset), charset );

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


/* Document the purpose of this class.
 *
 * @version 1.0
 * @author Timo Stich
 */

package org.columba.mail.coder;

import java.io.*;

public class NullDecoder extends Decoder {


    public NullDecoder()
    {
        coding = new String("null");
    }    

    public String decode( String input, String charset) throws UnsupportedEncodingException {
    	if( charset != null ) {
	    	return new String( input.getBytes(), charset );
    	}
    	return input;
    }
    
    public void decode( InputStream in, OutputStream out ) throws IOException {
    	byte[] buffer = new byte[1024];
    	int read;
    	
    	read = in.read(buffer);
    	while ( read == 1024 ) {    		
    		out.write(buffer);
	    	read = in.read(buffer);    		
    	}
    	
    	out.write( buffer, 0, read );
    	
    	in.close();
    	out.close();
    }


    

}