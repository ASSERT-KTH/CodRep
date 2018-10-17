@version $Id: MaxConcurrentSearchException.java,v 1.3 2004/05/07 05:57:48 dabbous Exp $

package org.tigris.scarab.util.word;

/* ================================================================
 * Copyright (c) 2003 CollabNet.  All rights reserved.
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
 * software developed by Collab.Net <http://www.Collab.Net/>."
 * Alternately, this acknowlegement may appear in the software itself, if
 * and wherever such third-party acknowlegements normally appear.
 * 
 * 4. The hosted project names must not be used to endorse or promote
 * products derived from this software without prior written
 * permission. For written permission, please contact info@collab.net.
 * 
 * 5. Products derived from this software may not use the "Tigris" or 
 * "Scarab" names nor may "Tigris" or "Scarab" appear in their names without 
 * prior written permission of Collab.Net.
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
 * individuals on behalf of Collab.Net.
 */ 

import org.tigris.scarab.tools.localization.L10NKeySet;
import org.tigris.scarab.tools.localization.L10NMessage;
import org.tigris.scarab.tools.localization.Localizable;
import org.tigris.scarab.tools.localization.LocalizationKey;
import org.tigris.scarab.util.ScarabException;

/**
    This class extends ScarabException and does not change its
    functionality.  It is thrown when the maximum number of concurrent
    searches are in process and another is requested.
    
    @author <a href="mailto:jmcnally@collab.net">John D. McNally</a>
    @version $Id: MaxConcurrentSearchException.java,v 1.2 2004/05/01 19:04:30 dabbous Exp $
*/
public class MaxConcurrentSearchException extends ScarabException
{
    /**
     * Constructs a new <code>MaxConcurrentSearchException</code> with specified 
     * detail message.
     *
     * @param msg the error message.
     */
    public MaxConcurrentSearchException(LocalizationKey l10nKey)
    {
        super(l10nKey);
    }

    /**
     * Constructs a new <code>MaxConcurrentSearchException</code> with specified 
     * detail message.
     *
     * @param msg the error message.
     */
    public MaxConcurrentSearchException(Localizable l10nMessage)
    {
        super(l10nMessage);
    }

    /**
     * Constructs a new <code>MaxConcurrentSearchException</code> with specified 
     * detail message.
     *
     * @param msg the error message.
     */
    public MaxConcurrentSearchException(Localizable l10nMessage, Throwable nested)
    {
        super(l10nMessage, nested);
    }

    /**
     * Constructs a new <code>MaxConcurrentSearchException</code> with specified 
     * resource and a list of parameters.
     * @param theKey the l10n error key.
     */
    public static ScarabException create(LocalizationKey theKey, Object[] theParams)
    {
        Localizable l10nMessage = new L10NMessage(theKey, theParams);
        return new MaxConcurrentSearchException(l10nMessage);
    }

 
    /**
     * Convenience method: Constructs a new <code>MaxConcurrentSearchException</code>
     * with specified resource, nested Throwable and an aritrary set of parameters.
     * @param theKey the l10n error key.
     */
    public static ScarabException create(LocalizationKey theKey, Throwable nested, Object[] theParams)
    {
        Localizable l10nMessage = new L10NMessage(theKey, theParams);
        ScarabException result = new MaxConcurrentSearchException(l10nMessage, nested);
        return result;
    }
}