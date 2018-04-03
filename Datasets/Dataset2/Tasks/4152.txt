@version $Revision: 1.5 $

/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
package org.jboss.logging;

import org.apache.log4j.Category;

/** An implementation of Log that routes msgs to a
log4j Category. This class is used to replace the Log
instances created via the legacy Log.createLog(Object)
The Log#log(String, String) method is implemented to send
pass the message onto the instance log4j Category.

@see #logToCategory(String, String, Category)

@author <a href="mailto:Scott_Stark@displayscape.com">Scott Stark</a>.
@version $Revision: 1.4 $
*/
public class LogToCategory extends Log
{
    private Category category;
    /** Wraps a log4j Category object to expose it as a legacy Log instance.
    */
    public LogToCategory(Category category)
    {
        super(category.getName());
        this.category = category;
    }
    /** A compatability contstructor that allows the Log.createLog(Object)
        to use the LogToCategory as the default type of Log. This
        ctor create a log4j Category using Category.getInstance(source.toString())
    */
    public LogToCategory(Object source)
    {
        super(source);
        this.category = Category.getInstance(source.toString());
    }

    public void log(String type, String message)
    {
        logToCategory(type, message, category);
    }

    /** Log a msg of a given Log type to the provided category.
    @param type, one of the Log "Information", "Debug", "Warning", "Error" strings.
    @param msg, the message to log
    @param category, the log4j Category instance to log the msg to
    */
    public static void logToCategory(String type, String msg, Category category)
    {
        char ctype = type.charAt(0);
        switch( ctype )
        {
            case 'W':
                category.warn(msg);
            break;
            case 'D':
                category.debug(msg);
            break;
            case 'E':
                category.error(msg);
            break;
            default:
                category.info(msg);
            break;
        }
    }
}