@version $Revision: 1.2 $

package org.jboss.logging;

import java.io.PrintStream;

import org.apache.log4j.AppenderSkeleton;
import org.apache.log4j.Category;
import org.apache.log4j.Priority;
import org.apache.log4j.spi.LoggingEvent;

/** A log4j Appender implementation that writes to the System.out and
System.err console streams. It also installs PrintStreams for System.out
and System.err to route logging through those objects to the log4j
system via a category named Default.

@author Scott_Stark@displayscape.com
@version $Revision: 1.1 $
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
        System.setOut(new Log4jStream(Priority.INFO, out));
        System.setErr(new Log4jStream(Priority.ERROR, err));
    }

    public void activateOptions()
    {
        super.activateOptions();
        category = Category.getInstance("Default");
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
            out.print(msg);
        else
            err.print(msg);
    }

    class Log4jStream extends PrintStream
    {
        Priority priority;
        Log4jStream(Priority priority, PrintStream ps)
        {
            super(ps);
            this.priority = priority;
        }
        public void println(String msg)
        {
            category.log(priority, msg);
        }
        public void println(Object msg)
        {
            category.log(priority, msg);
        }
    }
}