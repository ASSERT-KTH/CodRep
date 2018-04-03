Hashtable lProperties = (Hashtable) pParent.getKeyPropertyList().clone();

/*
* JBoss, the OpenSource J2EE webOS
*
* Distributable under LGPL license.
* See terms of license at gnu.org.
*/
package org.jboss.management.j2ee;

import java.io.Serializable;
import java.security.InvalidParameterException;
import java.util.Hashtable;

import javax.management.JMException;
import javax.management.MalformedObjectNameException;
import javax.management.MBeanServer;
import javax.management.ObjectName;

import javax.management.j2ee.EventProvider;
import javax.management.j2ee.StateManageable;
import javax.management.j2ee.StatisticsProvider;

import org.jboss.system.ServiceMBeanSupport;

/**
* JBoss specific implementation.
*
* @author Marc Fleury
**/
public abstract class J2EEManagedObject
   extends ServiceMBeanSupport
   implements javax.management.j2ee.J2EEManagedObject, Serializable
{
   // -------------------------------------------------------------------------
   // Static
   // -------------------------------------------------------------------------  
   
   private static String sDomainName = null;
//   protected static MBeanServer sServer = null;
   
   public static String getDomainName() {
      return sDomainName;
   }
   
/*   
   public static MBeanServer getServer() {
      return sServer;
   }
*/
   
   // -------------------------------------------------------------------------
   // Members
   // -------------------------------------------------------------------------  

   private ObjectName mParent = null;
   private ObjectName mName = null;

   // -------------------------------------------------------------------------
   // Constructors
   // -------------------------------------------------------------------------

   /**
   * Constructor for the root J2EEManagement object
   *
   * @param pDomainName Name of the domain
   * @param pType Type of the Managed Object which must be defined
   * @param pName Name of the Managed Object which must be defined
   *
   * @throws InvalidParameterException If the given Domain Name, Type or Name is null
   **/
   public J2EEManagedObject( String pDomainName, String pType, String pName )
      throws
         MalformedObjectNameException
   {
      if( pDomainName == null ) {
         throw new InvalidParameterException( "Domain Name must be set" );
      }
      sDomainName = pDomainName;
      Hashtable lProperties = new Hashtable();
      lProperties.put( "type", pType );
      lProperties.put( "name", pName );
      mName = new ObjectName( getDomainName(), lProperties );
      System.out.println( "J2EEManagedObject(), create root with name: " + mName );
   }
   
   /**
   * Constructor for any Managed Object except the root J2EEMangement.
   *
   * @param pType Type of the Managed Object which must be defined
   * @param pName Name of the Managed Object which must be defined
   * @param pParent Object Name of the parent of this Managed Object
   *                which must be defined
   *
   * @throws InvalidParameterException If the given Type, Name or Parent is null
   **/
   public J2EEManagedObject( String pType, String pName, ObjectName pParent )
      throws
         MalformedObjectNameException,
         InvalidParentException
   {
      try {
      Hashtable lProperties = pParent.getKeyPropertyList();
      System.out.println( "J2EEManagedObject(), parent properties: " + lProperties );
      System.out.println( "J2EEManagedObject(), parent type: " + lProperties.get( "type" ) );
      System.out.println( "J2EEManagedObject(), parent name: " + lProperties.get( "name" ) );
      lProperties.put( lProperties.get( "type" ), lProperties.get( "name" ) );
      lProperties.put( "type", pType );
      lProperties.put( "name", pName );
      mName = new ObjectName( getDomainName(), lProperties );
      System.out.println( "J2EEManagedObject(), properties: " + lProperties );
      setParent( pParent );
      }
      catch( Exception e ) {
         e.printStackTrace();
      }
   }

   // -------------------------------------------------------------------------
   // Properties (Getters/Setters)
   // -------------------------------------------------------------------------  

   public String getName() {
      return mName.toString();
   }
   
   public ObjectName getObjectName() {
      System.out.println( "J2EEManagedObject.getObjectName(), name: " + mName );
      return mName;
   }

   public ObjectName getObjectName( MBeanServer pServer, ObjectName pName ) {
      return getObjectName();
   }

   public boolean isStateManageable() {
      return this instanceof StateManageable;
   }

   public boolean isStatisticsProvider() {
      return this instanceof StatisticsProvider;
   }
   
   public boolean isEventProvider() {
      return this instanceof EventProvider;
   }
   
   public String toString() {
      return "J2EEManagedObject [ name: " + mName + ", parent: " + mParent + " ];";
   }
   
   public ObjectName getParent() {
      return mParent;
   }
   
   public void setParent( ObjectName pParent )
      throws
         InvalidParentException
   {
      if( pParent == null ) {
         throw new InvalidParameterException( "Parent must be set" );
      }
      mParent = pParent;
   }
   
   public void postRegister( java.lang.Boolean pRegistrationDone ) {
      System.out.println( "J2EEManagedObject.postRegister(), parent: " + mParent );
      if( pRegistrationDone.booleanValue() && mParent != null ) {
         try {
            // Notify the parent about its new child
            getServer().invoke(
               mParent,
               "addChild",
               new Object[] { mName },
               new String [] { ObjectName.class.getName() }
            );
            super.postRegister( pRegistrationDone );
         }
         catch( JMException jme ) {
            jme.printStackTrace();
            // Stop it because of the error
            super.postRegister( new Boolean( false ) );
         }
      }
   }
   
   public void addChild( ObjectName pChild ) {
      //AS ToDo: Remove later is just here to compile
   }
   public void removeChild( ObjectName pChild ) {
      //AS ToDo: Remove later is just here to compile
   }
}