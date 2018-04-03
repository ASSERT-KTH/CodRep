@version $Revision: 1.6 $

/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
package org.jboss.logging.log4j;

import java.io.PrintStream;

import org.apache.log4j.AppenderSkeleton;
import org.apache.log4j.Category;
import org.apache.log4j.Priority;
import org.apache.log4j.spi.LoggingEvent;
import org.apache.log4j.Layout;

/** A log4j Appender implementation that writes to the System.out and
System.err console streams. It also installs PrintStreams for System.out
and System.err to route logging through those objects to the log4j
system via a category named Default.

@author <a href="mailto:Scott_Stark@displayscape.com">Scott Stark</a>.
@version $Revision: 1.5 $
*/
public class ConsoleAppender extends AppenderSkeleton
{
    private Category category;
    private PrintStream out;
    private PrintStream err;

    /** Creates new ConsoleAppender */
    public ConsoleAppender()
    {
        out = System.out;
        err = System.err;
    }

    public void activateOptions()
    {
        super.activateOptions();
        category = Category.getInstance("Default");
        System.setOut(new CategoryStream(category, Priority.INFO, out));
        System.setErr(new CategoryStream(category, Priority.ERROR, err));
    }

    public boolean requiresLayout()
    {
        return true;
    }

    public void close()
    {
        if( out != null )
            System.setOut(out);
        out = null;
        if( err != null )
            System.setErr(err);
        err = null;
    }

    protected void append(LoggingEvent event)
    {
        String msg = this.layout.format(event);
        if( event.priority == Priority.ERROR )
            err.print(msg);
        else
            out.print(msg);
        if(this.layout.ignoresThrowable())
        {
            String[] s = event.getThrowableStrRep();
            if (s != null)
            {
        	    int len = s.length;
        	    for(int i = 0; i < len; i++)
                {
                    if( event.priority == Priority.ERROR )
                    {
        	            err.print(s[i]);
                	    err.print(Layout.LINE_SEP);
                    }
                    else
                    {
        	            out.print(s[i]);
        	            out.print(Layout.LINE_SEP);
                    }
                }
            }
        }
    }
}