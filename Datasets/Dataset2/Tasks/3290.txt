import org.columba.mail.message.Flags;

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


package org.columba.mail.folder;

import org.columba.mail.message.*;


public class MessageFolderInfo
{
    private Flags flags;
    private Flags permanentFlags;
    
    private int exists; // total number of messages
    
    private int recent; //  new messages

    private int uidValidity;
    private int uidNext;
    
    private int unseen;

    private boolean readWrite;
    
    
    public MessageFolderInfo()
    {}

    public void setFlags( Flags f )
    {
        flags = f;
    }

    public void setPermanentFlags( Flags f )
    {
        permanentFlags = f;
    }

    public void setExists( int i )
    {
        exists = i;
    }

    public void setRecent( int i )
    {
        recent = i;
    }

    public void setUnseen( int i )
    {
        unseen = i;
    }

    public void setUidValidity( int i )
    {
        uidValidity = i;
    }

    public void setUidNext( int i )
    {
        uidNext = i;
    }

    public void setReadWrite( boolean b )
    {
        readWrite = b;
    }
    
    

    public void incExists()
    {
	exists++;
    }
    public void incExists(int value)
    {
	exists+=value;
    }    
    public void decExists()
    {
	exists--;
    }
    public void decExists(int value)
    {
	exists-=value;
    }
    
    public void incRecent()
    {
	recent++;
    }
    public void decRecent()
    {
	recent--;
    }
    public void incUnseen()
    {
	unseen++;
    }
    public void decUnseen()
    {
	unseen--;
    }
    

    

    
    public Flags getFlags()
    {
        return flags;
    }

    public Flags getPermanentFlags()
    {
        return permanentFlags;
    }

    public int getExists()
    {
        return exists;
    }

    public int getRecent()
    {
        return recent;
    }

    public int getUidValidity()
    {
        return uidValidity;
    }

    public int getUidNext()
    {
        return uidNext;
    }

    public int getUnseen()
    {
        return unseen;
    }

    public boolean getReadWrite()
    {
        return readWrite;
    }
    
    
    
}