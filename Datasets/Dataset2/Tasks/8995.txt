trunkRamp.setTrunkListener(optimizedInvoker);

/***************************************
 *                                     *
 *  JBoss: The OpenSource J2EE WebOS   *
 *                                     *
 *  Distributable under LGPL license.  *
 *  See terms of license at gnu.org.   *
 *                                     *
 ***************************************/

package org.jboss.invocation.trunk.server.nbio;


import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.nio.channels.SelectionKey;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import javax.resource.spi.work.WorkManager;
import org.jboss.invocation.trunk.client.CommTrunkRamp;
import org.jboss.invocation.trunk.client.ConnectionManager;
import org.jboss.invocation.trunk.client.nbio.NonBlockingSocketTrunk;
import org.jboss.invocation.trunk.client.nbio.SelectionAction;
import org.jboss.invocation.trunk.client.nbio.SelectorManager;
import org.jboss.invocation.trunk.server.IServer;
import org.jboss.invocation.trunk.server.TrunkInvoker;
import org.jboss.logging.Logger;

/**
 * Provides a Non Blocking implemenation of the IServer interface.
 * 
 * Sets up a non-blocking ServerSocketChannel to accept NBIO client connections.
 *
 * @author    <a href="mailto:hiram.chirino@jboss.org">Hiram Chirino</a>
 */
public final class NonBlockingServer implements IServer
{

   /**
    * logger instance.
    */
   final static private Logger log = Logger.getLogger(NonBlockingServer.class);

   /**
    * If the TcpNoDelay option should be used on the socket.
    */
   private boolean enableTcpNoDelay = false;

   /**
    * The listening socket that receives incomming connections
    * for servicing.
    */
   private ServerSocketChannel serverSocket;

   /**
    * Manages the selector.
    */
   SelectorManager selectorManager;

   TrunkInvoker optimizedInvoker;

   private WorkManager workManager;

   public ServerSocket bind(
      TrunkInvoker optimizedInvoker,
      InetAddress address,
      int port,
      int connectBackLog,
      boolean enableTcpNoDelay,
      WorkManager workManager)
      throws IOException
   {
      this.optimizedInvoker = optimizedInvoker;
      this.enableTcpNoDelay = enableTcpNoDelay;
      this.workManager = workManager;

      selectorManager = SelectorManager.getInstance(ConnectionManager.oiThreadGroup);

      // Create a new non-blocking ServerSocketChannel, bind it to port 8000, and
      // register it with the Selector
      serverSocket = ServerSocketChannel.open(); // Open channel
      serverSocket.configureBlocking(false); // Non-blocking
      serverSocket.socket().bind(new InetSocketAddress(address, port), connectBackLog); // Bind to port      
      //serverSocket.socket().setSoTimeout(SO_TIMEOUT);
      serverSocket.register(selectorManager.getSelector(), SelectionKey.OP_ACCEPT, new AcceptConnectionAction());

      return serverSocket.socket();
   }

   public void start() throws IOException
   {
      selectorManager.start();
   }

   public void stop() throws IOException
   {
      selectorManager.stop();
   }

   class AcceptConnectionAction implements SelectionAction
   {

      public void service(SelectionKey selection)
      {
         // Activity on the ServerSocketChannel means a client
         // is trying to connect to the server.
         if (!selection.isAcceptable())
            return;

         ServerSocketChannel server = (ServerSocketChannel) selection.channel();

         try
         {
            if (log.isTraceEnabled())
               log.trace("Accepting client connection");

            // Accept the client connection
            SocketChannel client = server.accept();
            NonBlockingSocketTrunk trunk = new NonBlockingSocketTrunk(client, selectorManager.getSelector());
            CommTrunkRamp trunkRamp = new CommTrunkRamp(trunk, workManager);
            trunk.setCommTrunkRamp(trunkRamp);
            trunkRamp.setTrunkListner(optimizedInvoker);
            trunk.start();

         }
         catch (IOException e)
         {
            log.debug("Error establishing connection with client: ", e);
         }
      }
   }

}
// vim:expandtab:tabstop=3:shiftwidth=3