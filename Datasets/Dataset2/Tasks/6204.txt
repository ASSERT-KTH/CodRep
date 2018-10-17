ByteArrayOutputStream baos = new ByteArrayOutputStream(1000);

/***************************************
 *                                     *
 *  JBoss: The OpenSource J2EE WebOS   *
 *                                     *
 *  Distributable under LGPL license.  *
 *  See terms of license at gnu.org.   *
 *                                     *
 ***************************************/
package org.jboss.invocation.trunk.client;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.rmi.MarshalledObject;

import org.jboss.logging.Logger;

/**
 * This is the response message that will be sent of the socket
 *
 * @author    <a href="mailto:hiram.chirino@jboss.org">Hiram Chirino</a>
 */
public class TrunkResponse
{
   final static private Logger log = Logger.getLogger(TrunkResponse.class);

   final static byte RESULT_VOID = 1;
   final static byte RESULT_OBJECT = 2;
   final static byte RESULT_EXCEPTION = 3;
   private static ClassLoader classLoader = TunkRequest.class.getClassLoader();

   public Integer correlationRequestId;
   public MarshalledObject result;
   public MarshalledObject exception;

   public TrunkResponse()
   {
   }
   public TrunkResponse(TunkRequest request)
   {
      correlationRequestId = request.requestId;
   }

   public Object evalThrowsException() throws Exception
   {
      if (exception != null)
      {
         Throwable e = (Throwable)exception.get();
         if (e instanceof Exception)
         {
            throw (Exception) e;
         }
         else
         {
            log.debug("Protocol violation: unexpected exception found in response: ", e);
            throw new IOException("Protocol violation: unexpected exception found in response: " + exception);
         }
      }
      return result.get();
   }

   public Object evalThrowsThrowable() throws Throwable
   {
      if (exception != null)
      {
         throw (Throwable)exception.get();
      }
      return result.get();
   }

   public byte[] serialize() throws IOException
   {
      ByteArrayOutputStream baos = new ByteArrayOutputStream();
      ObjectOutputStream out = new CustomObjectOutputStream(baos);

      if (correlationRequestId == null)
      {
         out.writeByte(0);
      }
      else
      {
         out.writeByte(1);
         out.writeInt(correlationRequestId.intValue());
      }

      if (exception != null)
      {
         out.writeByte(RESULT_EXCEPTION);
         out.writeObject(exception);
      }
      else if (result == null)
      {
         out.writeByte(RESULT_VOID);
      }
      else
      {
         out.writeByte(RESULT_OBJECT);
         out.writeObject(result);
      }
      out.close();
      return baos.toByteArray();
   }

   public void deserialize(byte data[]) throws IOException, ClassNotFoundException
   {
      ByteArrayInputStream bais = new ByteArrayInputStream(data);
      ObjectInputStream in = new CustomObjectInputStreamWithClassloader(bais, classLoader);

      if (in.readByte() == 1)
         correlationRequestId = new Integer(in.readInt());

      byte responseType = in.readByte();
      switch (responseType)
      {
         case RESULT_VOID :
            result = null;
            exception = null;
            break;
         case RESULT_EXCEPTION :
            result = null;
            exception = (MarshalledObject) in.readObject();
            break;
         case RESULT_OBJECT :
            exception = null;
            result = (MarshalledObject) in.readObject();
            break;
         default :
            throw new IOException("Protocol Error: Bad response type code '" + responseType + "' ");
      }

      in.close();
   }

   public String toString()
   {
      return "[correlationRequestId:" + correlationRequestId + ",result:" + result + ",exception:" + exception + "]";
   }

}