if( "J2EEApplication".equals( lType ) ) {

package org.jboss.management.j2ee;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Hashtable;
import java.util.List;

import javax.management.MalformedObjectNameException;
import javax.management.ObjectName;

/**
* Is the access point to management information for a single J2EE Server
* Core implementation representing a logical core server of one instance
* of a J2EE platform product.
*
* @author <a href="mailto:andreas@jboss.org">Andreas Schaefer</a>
**/
public class J2EEServer
  extends J2EEManagedObject
  implements J2EEServerMBean
{
   // -------------------------------------------------------------------------
   // Members
   // -------------------------------------------------------------------------
   
   private List mApplications = new ArrayList();
   
   private List mResources = new ArrayList();
   
   private List mNodes = new ArrayList();
   
   private List mJVMs = new ArrayList();
   
   private String mJ2eeVendor = null;
   
   // -------------------------------------------------------------------------
   // Constructors
   // -------------------------------------------------------------------------
   
   public J2EEServer( String pName, ObjectName pDomain, String pJ2eeVendor )
      throws
         MalformedObjectNameException,
         InvalidParentException
   {
      super( "J2EEServer", pName, pDomain );
      mJ2eeVendor = pJ2eeVendor;
   }
   
   public J2EEServer(
      String pName,
      ObjectName pDomain,
      ObjectName[] pApplications,
      ObjectName[] pResources,
      ObjectName[] pNodes,
      ObjectName[] pJVMs,
      String pJ2eeVendor
   )
      throws
         MalformedObjectNameException,
         InvalidParentException
   {
      super( "J2EEServer", pName, pDomain );
      mApplications.addAll( Arrays.asList( pApplications ) );
      mResources.addAll( Arrays.asList( pResources ) );
      mNodes.addAll( Arrays.asList( pNodes ) );
      mJVMs.addAll( Arrays.asList( pJVMs ) );
      mJ2eeVendor = pJ2eeVendor;
   }
   
   // -------------------------------------------------------------------------
   // Properties (Getters/Setters)
   // -------------------------------------------------------------------------  

   public ObjectName[] getApplications() {
      return (ObjectName[]) mApplications.toArray( new ObjectName[ 0 ] );
   }

   public ObjectName getApplication( int pIndex ) {
      if( pIndex >= 0 && pIndex < mApplications.size() ) {
         return (ObjectName) mApplications.get( pIndex );
      }
      return null;
   }

   public ObjectName[] getNodes() {
      return (ObjectName[]) mNodes.toArray( new ObjectName[ 0 ] );
   }

   public ObjectName getNode( int pIndex ) {
      if( pIndex >= 0 && pIndex < mNodes.size() ) {
         return (ObjectName) mNodes.get( pIndex );
      }
      return null;
   }

   public ObjectName[] getResources() {
      return (ObjectName[]) mResources.toArray( new ObjectName[ 0 ] );
   }

   public ObjectName getResource( int pIndex ) {
      if( pIndex >= 0 && pIndex < mResources.size() ) {
         return (ObjectName) mResources.get( pIndex );
      }
      return null;
   }

   public ObjectName[] getJavaVMs() {
      return (ObjectName[]) mJVMs.toArray( new ObjectName[ 0 ] );
   }

   public ObjectName getJavaVM( int pIndex ) {
      if( pIndex >= 0 && pIndex < mJVMs.size() ) {
         return (ObjectName) mJVMs.get( pIndex );
      }
      return null;
   }

   public String getJ2eeVendor() {
      return mJ2eeVendor;
   }
   
   public void addChild( ObjectName pChild ) {
      Hashtable lProperties = pChild.getKeyPropertyList();
      String lType = lProperties.get( "type" ) + "";
      if( "Application".equals( lType ) ) {
         mApplications.add( pChild );
      } else if( "Node".equals( lType ) ) {
         mNodes.add( pChild );
      } else if( "JVM".equals( lType ) ) {
         mJVMs.add( pChild );
      } else if( "Resource".equals( lType ) ) {
         mResources.add( pChild );
      }
   }
   
   public void removeChild( ObjectName pChild ) {
      //AS ToDo
   }

   public String toString() {
      return "J2EEServer { " + super.toString() + " } [ " +
         "applications: " + mApplications +
         ", resources: " + mResources +
         ", nodes: " + mNodes +
         ", JVMs: " + mJVMs +
         ", J2EE vendor: " + mJ2eeVendor +
         " ]";
   }

}