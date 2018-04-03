throw new InvalidParameterException( "There IP-Address must always be defined" );

/*
* JBoss, the OpenSource J2EE webOS
*
* Distributable under LGPL license.
* See terms of license at gnu.org.
*/
package org.jboss.management.j2ee;

import java.security.InvalidParameterException;

import javax.management.MalformedObjectNameException;
import javax.management.ObjectName;

import javax.management.j2ee.Port;

/**
 * @author Marc Fleury
 **/
public class IpAddress
   extends J2EEManagedObject
   implements javax.management.j2ee.IpAddress
{
   // -------------------------------------------------------------------------
   // Members
   // -------------------------------------------------------------------------  

   private String mAddress;

   // -------------------------------------------------------------------------
   // Constructors
   // -------------------------------------------------------------------------

   /**
    * @throws InvalidParameterException If given list is null or empty
    **/
   public IpAddress( String pName, ObjectName pNode, String pAddress )
      throws
         MalformedObjectNameException,
         InvalidParentException
   {
      super( "IpAddress", pName, pNode );
      if( pAddress == null || pAddress.length() == 0 ) {
         throw new InvalidParameterException( "There driver must always be defined" );
      }
      mAddress = pAddress;
   }

   // -------------------------------------------------------------------------
   // Properties (Getters/Setters)
   // -------------------------------------------------------------------------  

   public String getAddress() {
      return mAddress;
   }

   public String toString() {
      return "IpAddress [ " +
         "IpAddress: " + getAddress() +
         " ]";
   }
}