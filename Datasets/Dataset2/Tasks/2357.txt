import java.util.Vector;

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


/** Document the purpose of this class.
 *
 * @version 1.0
 * @author 
 */

package org.columba.mail.coder;

import java.util.*;

public class CoderRouter
{
    static Vector encoderList;
    static Vector decoderList;
    static Decoder nullDecoder;
    static Encoder nullEncoder;
    
    public CoderRouter()
    {
        encoderList = new Vector();
        decoderList = new Vector();

        nullDecoder = new NullDecoder();
        nullEncoder = new NullEncoder();
    }


    static public Decoder getDecoder( String encoding )
    {
        int size = decoderList.size();
        Decoder actDecoder;
        
        if( encoding == null ) return (Decoder) nullDecoder.clone();

        encoding = encoding.toLowerCase();

        for( int i=0; i<size; i++ ) {
            actDecoder = (Decoder) decoderList.get(i);

            if( actDecoder.getCoding().equals( encoding ) ) {
            return (Decoder) actDecoder.clone();
            }
        }

        return (Decoder) nullDecoder.clone();
    }
    static public Encoder getEncoder( String encoding )
    {
        int size = encoderList.size();
        Encoder actEncoder;

        if( encoding == null ) return (Encoder) nullEncoder.clone();

        encoding = encoding.toLowerCase();
        
        for( int i=0; i<size; i++ ) {
            actEncoder = (Encoder) encoderList.get(i);

            if( actEncoder.getCoding().equals( encoding ) ) {
                return (Encoder) actEncoder.clone();
            }
        }

        return (Encoder) nullEncoder.clone();
    }

    
    static public void addEncoder( Encoder encoder )
    {
        encoderList.add( encoder );
    }

    static public void addDecoder( Decoder decoder )
    {
        decoderList.add( decoder );
    }
    

    
}

