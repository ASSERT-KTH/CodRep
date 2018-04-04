public void sendRequest(TrunkRequest request) throws IOException;

/***************************************
 *                                     *
 *  JBoss: The OpenSource J2EE WebOS   *
 *                                     *
 *  Distributable under LGPL license.  *
 *  See terms of license at gnu.org.   *
 *                                     *
 ***************************************/

package org.jboss.invocation.trunk.client;

import java.io.IOException;

/**
 * This is the interface to "trunk" of the main message flow.
 * You can send requests, responses, and receive them too.
 * 
 * Every trunk is associated with only one CommTrunkRamp.  A trunk
 * ramp takes care of multiplexing the sending and receiving of requests 
 * and responses.
 * 
 * @author <a href="mailto:hiram.chirino@jboss.org">Hiram Chirino</a>
 */
public interface ICommTrunk
{
   /**
    * Sends a response down the trunk, should block until we know the 
    * send will succeed.
    */
   public void sendResponse(TrunkResponse response) throws IOException;

   /**
    * Sends a request down the trunk, should block until we know the 
    * send will succeed.
    */
   public void sendRequest(TunkRequest request) throws IOException;

   /**
    * Set the CommTrunkRamp that is CommTrunk will be using.
    */
   public void setCommTrunkRamp(CommTrunkRamp ramp);

   /**
    * Get the CommTrunkRamp that is CommTrunk is using.
    */
   public CommTrunkRamp getCommTrunkRamp();

   /**
    * Is the CommTrunk connection valid??  Can it be used
    * to send and receive data?
    */
   public boolean isConnected();

}