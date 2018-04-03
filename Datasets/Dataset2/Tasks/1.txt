te.setFrom(u.getName(), u.getEmail());

package org.tigris.scarab.tools;

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

import java.util.List;
import java.util.LinkedList;
import java.util.Iterator;
import javax.mail.SendFailedException;

import org.apache.fulcrum.template.TemplateContext;
import org.apache.fulcrum.template.DefaultTemplateContext;
import org.apache.fulcrum.template.TemplateEmail;

import org.apache.turbine.Turbine;
import org.tigris.scarab.om.ScarabUser;
import org.tigris.scarab.services.module.ModuleEntity;

/**
 * Sends a notification email.
 */
public class Email
{
    public static boolean sendEmail( TemplateContext context, 
                                     ModuleEntity module, Object fromUser,
                                     List toUsers, List ccUsers,
                                     String subject, String template )
        throws Exception
    {
        boolean success = true;
        TemplateEmail te = new TemplateEmail();
        if ( context == null ) 
        {
            context = new DefaultTemplateContext();
        }        
        te.setContext(context);
        
        if (fromUser instanceof ScarabUser)
        {
            ScarabUser u = (ScarabUser)fromUser;
            te.setFrom(u.getFirstName() + u.getLastName(), u.getEmail());
        }
        else
        {
            // assume string
            String key = (String)fromUser;	    
            if (fromUser == null)
            {
                key = "scarab.email.default";
            } 
            
            te.setFrom(Turbine.getConfiguration().getString
                       (key + ".fromName", "Scarab System"), 
                       Turbine.getConfiguration().getString
                       (key + ".fromAddress",
                        "help@scarab.tigris.org"));
        }
        
        if (subject == null)
        {
            te.setSubject((Turbine.getConfiguration().
                           getString("scarab.email.default.subject")));
        }
        else
        {
            te.setSubject(subject);
        }
        
        if (template == null)
        {
            te.setTemplate(Turbine.getConfiguration().
                           getString("scarab.email.default.template"));
        }
        else
        {
            te.setTemplate(template);
        }
        
        Iterator iter = toUsers.iterator();
        while ( iter.hasNext() ) 
        {
            ScarabUser toUser = (ScarabUser)iter.next();
            te.addTo(toUser.getEmail(),
                     toUser.getFirstName() + " " + toUser.getLastName());
        }
        
        if (ccUsers != null)
        {
            iter = ccUsers.iterator();
            while ( iter.hasNext() ) 
            {
                ScarabUser ccUser = (ScarabUser)iter.next();
                te.addCc(ccUser.getEmail(),
                         ccUser.getFirstName() + " " + ccUser.getLastName());
            }
        }
        
        String archiveEmail = module.getArchiveEmail();
        if (archiveEmail != null && archiveEmail.trim().length() > 0)
        {
            te.addCc(archiveEmail, null);
        }
        
        try
        {
            te.sendMultiple();
        }
        catch (SendFailedException e)
        {
            success = false;
        }
        return success;
    }

    /**
     * Single user recipient.
     */ 
    public static boolean sendEmail( TemplateContext context, ModuleEntity module,
                                  Object fromUser, ScarabUser toUser, 
                                  String subject, String template )
        throws Exception
    {
        List toUsers = new LinkedList();
        toUsers.add(toUser);
        return sendEmail( context, module, fromUser, toUsers, null, subject, template);
    }
}