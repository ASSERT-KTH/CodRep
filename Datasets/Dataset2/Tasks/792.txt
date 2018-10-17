ramp.setTrunkListener(this);

/***************************************
 *                                     *
 *  JBoss: The OpenSource J2EE WebOS   *
 *                                     *
 *  Distributable under LGPL license.  *
 *  See terms of license at gnu.org.   *
 *                                     *
 ***************************************/

package org.jboss.invocation.trunk.client.nbio;


import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;
import javax.resource.spi.work.WorkManager;
import org.jboss.invocation.trunk.client.AbstractClient;
import org.jboss.invocation.trunk.client.CommTrunkRamp;
import org.jboss.invocation.trunk.client.ConnectionManager;
import org.jboss.invocation.trunk.client.ICommTrunk;
import org.jboss.invocation.trunk.client.ServerAddress;
import org.jboss.logging.Logger;

/**
 * Provides a Non-Blocking implemenation for clients running on >= 1.4 JVMs.
 * 
 * It connects to the server with a SocketChannel and sets up a Non-blocking
 * ICommTrunk to handle the IO protocol.
 * 
 * @author    <a href="mailto:hiram.chirino@jboss.org">Hiram Chirino</a>
 */
public class NonBlockingClient extends AbstractClient
{
   private final static Logger log = Logger.getLogger(NonBlockingClient.class);

   private NonBlockingSocketTrunk trunk;
   private SocketChannel socket;
   private ServerAddress serverAddress;
   private SelectorManager selectorManager;
   
   public void connect(ServerAddress serverAddress, 
                       ThreadGroup threadGroup) throws IOException
   {
      this.serverAddress = serverAddress;
      boolean tracing = log.isTraceEnabled();
      if (tracing)
         log.trace("Connecting to : " + serverAddress);

      selectorManager = SelectorManager.getInstance(ConnectionManager.oiThreadGroup);

      socket = SocketChannel.open();
      socket.configureBlocking(true); // Make the connect be blocking.
      socket.connect(new InetSocketAddress(serverAddress.address, serverAddress.port));
      socket.configureBlocking(false); // Make the connect be non-blocking.
            
     // serverAddress.address, serverAddress.port);
      socket.socket().setTcpNoDelay(serverAddress.enableTcpNoDelay);

      trunk = new NonBlockingSocketTrunk(socket, selectorManager.getSelector());
      CommTrunkRamp ramp = new CommTrunkRamp(trunk, workManager);
      trunk.setCommTrunkRamp(ramp);
      ramp.setTrunkListner(this);
      
      if (tracing)
         log.trace("Connection established.");
      
   }

   public ServerAddress getServerAddress()
   {
      return serverAddress;
   }

   public ICommTrunk getCommTrunk()
   {
      return trunk;
   }

   public void start()
   {
      trunk.start();
      selectorManager.start();
   }

   public void stop()
   {
      trunk.stop();
      selectorManager.stop();
   }
}