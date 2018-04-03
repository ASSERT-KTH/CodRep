@version $Id: ModifyAttributes.java,v 1.20 2002/01/15 21:19:19 elicia dead $

package org.tigris.scarab.actions.admin;

/* ================================================================
 * Copyright (c) 2000-2001 CollabNet.  All rights reserved.
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

import java.util.List;
import java.util.ArrayList;

// Turbine Stuff 
import org.apache.turbine.RunData;
import org.apache.turbine.TemplateContext;
import org.apache.torque.om.ObjectKey;
import org.apache.torque.om.NumberKey;
import org.apache.turbine.tool.IntakeTool;
import org.apache.fulcrum.intake.model.Group;
import org.apache.fulcrum.intake.model.Field;
import org.apache.fulcrum.intake.model.BooleanField;

// Scarab Stuff
import org.tigris.scarab.actions.base.RequireLoginFirstAction;
import org.tigris.scarab.om.Attribute;
import org.tigris.scarab.om.AttributeOption;
import org.tigris.scarab.util.ScarabConstants;
import org.tigris.scarab.util.ScarabException;
import org.tigris.scarab.tools.ScarabRequestTool;

/**
    This class will store the form data for a project modification
        
    @author <a href="mailto:jon@collab.net">Jon S. Stevens</a>
    @version $Id: ModifyAttributes.java,v 1.19 2001/10/20 00:51:04 jon Exp $
*/
public class ModifyAttributes extends RequireLoginFirstAction
{
    /**
     * On the admin,AttributeShow.vm page, when you click the button,
     * this will get the right Attribute from the database and put it into
     * the $scarabR tool.
     */
    public void doSelectattribute( RunData data, TemplateContext context ) 
        throws Exception
    {
        String template = data.getParameters()
            .getString(ScarabConstants.TEMPLATE, null);
        String nextTemplate = data.getParameters().getString(
            ScarabConstants.NEXT_TEMPLATE, template );

        IntakeTool intake = (IntakeTool)context
            .get(ScarabConstants.INTAKE_TOOL);

        Field id = intake.get("Attribute", IntakeTool.DEFAULT_KEY).get("Id");
        id.setRequired(true);
        // FIXME: Add some security checking to make sure that the
        // User can actually edit a particular Attribute.
        if ( id.isValid() ) 
        {
            setTarget(data, nextTemplate);                
        }
    }

    /**
     * Used on AttributeEdit.vm to modify Attribute Name/Description/Type
     * Use doAddormodifyattributeoptions to modify the options.
     */
    public void doModifyattributedata( RunData data, TemplateContext context )
        throws Exception
    {
        IntakeTool intake = (IntakeTool)context
           .get(ScarabConstants.INTAKE_TOOL);

        if ( intake.isAllValid() )
        {
            Group attribute = intake.get("Attribute", IntakeTool.DEFAULT_KEY);
            Group attributeType = intake.get("AttributeType", IntakeTool.DEFAULT_KEY);

            String attributeID = attribute.get("Id").toString();
            String attributeName = attribute.get("Name").toString();
            String attributeDesc = attribute.get("Description").toString();
            String attributeTypeID = attributeType.get("AttributeTypeId").toString();

            Attribute attr = Attribute.getInstance((ObjectKey)new NumberKey(attributeID));
            attr.setName(attributeName);
            attr.setDescription(attributeDesc);
            attr.setTypeId(new NumberKey(attributeTypeID));
            attr.save();
        }
    }

    /**
     * Used on AttributeEdit.vm to change the name of an existing
     * AttributeOption or add a new one if the name doesn't already exist.
     */
    public synchronized void 
        doAddormodifyattributeoptions( RunData data, TemplateContext context )
        throws Exception
    {
        IntakeTool intake = (IntakeTool)context
           .get(ScarabConstants.INTAKE_TOOL);

        if ( intake.isAllValid() ) 
        {
            Attribute attribute = ((ScarabRequestTool)context
                .get(ScarabConstants.SCARAB_REQUEST_TOOL))
                    .getRModuleAttribute().getAttribute();

            AttributeOption option = null;
            List attributeOptions = new ArrayList (attribute
                .getAttributeOptions());
            // go in reverse because we may be removing from the list
            for (int i=attributeOptions.size()-1; i>=0; i--) 
            {
                option = (AttributeOption)attributeOptions.get(i);
                Group group = intake.get("AttributeOption", 
                                         option.getQueryKey());
                // in case the template is not showing all the options at once
                if ( group != null ) 
                {
                    // there could be an error with attempting to assign
                    // an invalid parent attribute option to an attribute
                    // option.
                    try
                    {
                        group.setProperties(option);
                    }
                    catch (Exception se)
                    {
                        intake.remove(group);
                        data.setMessage(se.getMessage());
                        return;
                    }

                    // check for a deleted flag.  AttributeOptions are marked
                    // as deleted.
 /*                   BooleanField deletedField = 
                        (BooleanField)group.get("Deleted");
                    if ( deletedField != null && deletedField.booleanValue() ) 
                    {
                        // remove from the Attribute's list
                        attributeOptions.remove(i);
                    }
*/
                    option.save();

                    // we need this because we are accepting duplicate
                    // numeric values and resorting, so we do not want
                    // to show the actual value entered by the user.
                    intake.remove(group);
                }
            }
//            attribute.sortOptions(attributeOptions);

            // was a new option added?
            option = AttributeOption.getInstance();
            Group group = intake.get("AttributeOption", 
                                     option.getQueryKey());
            if ( group != null ) 
            {
                try
                {
                    group.setProperties(option);
                }
                catch (Exception se)
                {
                    intake.remove(group);
                    data.setMessage(se.getMessage());
                    return;
                }
                if ( option.getName() != null 
                     && option.getName().length() != 0 ) 
                {
                    try
                    {
                        attribute.addAttributeOption(option);
                    }
                    catch (ScarabException se)
                    {
                        data.setMessage("Please select a unique name.");
                    }
                }

                // we need this because we are accepting duplicate
                // numeric values and resorting, so we do not want
                // to show the actual value entered by the user.
                intake.remove(group);

                for (int i=attributeOptions.size()-1; i>=0; i--) 
                {
                    option = (AttributeOption)attributeOptions.get(i);
                    group = intake.get("AttributeOption", 
                                             option.getQueryKey());
                    // in case the template is not showing all the options
                    if ( group != null ) 
                    {
                        intake.remove(group);
                    }
                }
            }                           
        }
    }

    /**
     * Manages clicking of the AllDone button
     */
    public void doAlldone( RunData data, TemplateContext context ) throws Exception
    {
        String nextTemplate = data.getParameters().getString(
            ScarabConstants.NEXT_TEMPLATE );

        setTarget(data, nextTemplate);
    }
    
    /**
        This manages clicking the cancel button
    */
    public void doCancel( RunData data, TemplateContext context ) throws Exception
    {
        data.setMessage("Changes were not saved!");
    }
    
    /**
        does nothing.
    */
    public void doPerform( RunData data, TemplateContext context ) throws Exception
    {
        doCancel(data, context);
    }
}