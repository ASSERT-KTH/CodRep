public void close() throws IOException {

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.mail.folder.headercache;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.ObjectInputStream;


/**
 * Object stream reader used by header-cache.
 * <p>
 * To make this more failsafe, ObjectWriter is using a ".backup" file.
 * 
 * @see ObjectWriter
 * 
 * @author fdietz
 */
public class ObjectReader {
    private static final int NULL = 0;
    private static final int STRING = 1;
    private static final int DATE = 2;
    private static final int BOOLEAN = 3;
    private static final int INTEGER = 4;
    private static final int COLOR = 5;
    private static final int OBJECT = 6;
    protected File file;
    protected FileInputStream istream;
    protected ObjectInputStream ois;
    protected File newFile;

    public ObjectReader(File file) throws Exception {
        this.file = file;
		
        istream = new FileInputStream(file.getPath());
        ois = new ObjectInputStream(new BufferedInputStream(istream));
        
    }

    public String readString() throws IOException{
    	return ois.readUTF();
    }
    
    public int readInt() throws IOException {
    	return ois.readInt();
    }
    
    public long readLong() throws IOException {
    	return ois.readLong();
    }
    
    public Object readObject() throws IOException, ClassNotFoundException {
    	return ois.readObject();	
    }
    
    /*
    public Object readObject() throws Exception {
        // if no data available
        if (ois.available()==0) return null;
        
        int classCode = ois.readInt();

        switch (classCode) {
        case NULL:
            return null;

        case STRING:
            return ois.readUTF();

        case INTEGER:
            return new Integer(ois.readInt());

        case BOOLEAN:
            return Boolean.valueOf(ois.readBoolean());

        case DATE:
            return new Date(ois.readLong());

        case COLOR: // ColorFactory makes sure that only one instance

            // of the same color exists
            return ColorFactory.getColor(ois.readInt());

        default: // some unspecified Object

            return ois.readObject();
        }
    }
    */

    public void close() throws Exception {
        ois.close();
        istream.close();
    }
}