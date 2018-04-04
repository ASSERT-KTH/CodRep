+ className + '\'', e); //EXCEPTION

package org.tigris.scarab.da;

/* ================================================================
 * Copyright (c) 2000 CollabNet.  All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 * 
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 * 
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 * 
 * 3. The end-user documentation included with the redistribution, if
 * any, must include the following acknowlegement: "This product includes
 * software developed by CollabNet (http://www.collab.net/)."
 * Alternately, this acknowlegement may appear in the software itself, if
 * and wherever such third-party acknowlegements normally appear.
 * 
 * 4. The hosted project names must not be used to endorse or promote
 * products derived from this software without prior written
 * permission. For written permission, please contact info@collab.net.
 * 
 * 5. Products derived from this software may not use the "Tigris" name
 * nor may "Tigris" appear in their names without prior written
 * permission of CollabNet.
 * 
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL COLLAB.NET OR ITS CONTRIBUTORS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
 * IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 * ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * ====================================================================
 * 
 * This software consists of voluntary contributions made by many
 * individuals on behalf of CollabNet.
 */

import java.util.HashMap;
import java.util.Map;

import org.apache.commons.lang.exception.NestableError;

import org.apache.turbine.Turbine;

/**
 * A lookup interface for the data access layer classes.  Use instead
 * of Fulcrum for simplicity.  Migration to an Avalon-based or other
 * "standard" API is a longer term possibility.
 */
public class DAFactory
{
    private static Map instances = new HashMap();

    public static AttributeAccess getAttributeAccess()
    {
        return (AttributeAccess) lookup("AttributeAccess");
    }

    /**
     * Gets a handle to one of our data access classes, in our
     * configuration prefixed with <code>dataaccess</code> and
     * sufffixed with <code>classname</code>
     * (e.g. dataaccess.AttributeAccess.classname =
     * org.tigris.scarab.da.ScarabAttributeAccess).
     *
     * @param identifier Which data access API to get a handle for.
     * @throws LookupError If a ClassNotFoundException would normally
     * be thrown.
     * @throws LinkageError
     */
    private static Object lookup(String identifier)
    {
        Object da = instances.get(identifier);
        if (da == null)
        {
            // There is an implicit race condition here.  Worst case
            // we create extra instances of our DA impl, and/or more
            // than one HashMap.  In either case, the cost of the
            // waste is minimal.
            Map map = new HashMap(instances);
            String className = Turbine.getConfiguration()
                .getString("dataaccess." + identifier + ".classname");
            try
            {
                da = Class.forName(className).newInstance();
                map.put(identifier, da);
                instances = map;
            }
            catch (Exception e)
            {
                throw new LookupError("Unable to create instantance of class '"
                                      + className + '\'', e);
            }
        }
        return da;
    }

    private static class LookupError extends NestableError
    {
        public LookupError(String msg, Throwable t)
        {
            super(msg, t);
        }
    }
}