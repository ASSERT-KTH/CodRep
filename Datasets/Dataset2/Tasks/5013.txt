ScarabUser user = (ScarabUser)TurbineSecurity.getUser(username);

package org.tigris.scarab.pipeline;

import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

import org.apache.commons.configuration.Configuration;
import org.apache.fulcrum.security.TurbineSecurity;
import org.apache.turbine.RunData;
import org.apache.turbine.Turbine;
import org.apache.turbine.TurbineException;
import org.apache.turbine.ValveContext;
import org.apache.turbine.pipeline.AbstractValve;
import org.tigris.scarab.om.ScarabUser;
import org.tigris.scarab.util.Log;

/*
 * This valve will try to automatically login an Anonymous user if there is no user authenticated.
 * The user and password will be set in scarab.user.anonymous and scarab.anonymous.password
 * If scarab.anonymous.username does not exists, the valve will just pass control to the following
 * through the pipeline.
 * 
 */
public class AnonymousLoginValve extends AbstractValve
{
    private final static Set nonAnonymousTargets = new HashSet();
    private String username = null;
    private String password = null;

    /**
     * Initilizes the templates that will not make an automatical
     * anonymous login.
     */
    public void initialize() throws Exception
    {
        Configuration conf = Turbine.getConfiguration();
        username = (String)conf.getProperty("scarab.anonymous.username");
        if (username != null) {
	        password = (String)conf.getProperty("scarab.anonymous.password");
	        nonAnonymousTargets.add("Index.vm");
	        nonAnonymousTargets.add("Logout.vm");
	        nonAnonymousTargets.add(conf.getProperty("template.login"));
	        nonAnonymousTargets.add(conf.getProperty("template.homepage"));
	        nonAnonymousTargets.add("Register.vm");
	        nonAnonymousTargets.add("ForgotPassword.vm");
        }
    }
    
    /* 
     * Invoked by the Turbine's pipeline, as defined in scarab-pipeline.xml
     * @see org.apache.turbine.pipeline.AbstractValve#invoke(org.apache.turbine.RunData, org.apache.turbine.ValveContext)
     */
    public void invoke(RunData data, ValveContext context) throws IOException, TurbineException
    {
        String target = data.getTarget();
        if (null != username && !nonAnonymousTargets.contains(target) && target.indexOf("help,") == -1)
        {
	        // If there's no user, we will login as Anonymous.
	        ScarabUser user = (ScarabUser)data.getUserFromSession();
	        if (null == user || user.getUserId() == null)
	            anonymousLogin(data, context);
        }
        context.invokeNext(data);        
    }

    /**
     * Logs the user defined as anonymous in the system.
     * @param data
     * @param context
     */
    private void anonymousLogin(RunData data, ValveContext context)
    {
        try
        {
            ScarabUser user = (ScarabUser)TurbineSecurity.getAuthenticatedUser(username, password);
            data.setUser(user);
            user.setHasLoggedIn(Boolean.TRUE);
            user.updateLastLogin();
            data.save();            
        }
        catch (Exception e)
        {
            Log.get().error("anonymousLogin failed to login anonymously: " + e.getMessage());
        }
        
    }

}