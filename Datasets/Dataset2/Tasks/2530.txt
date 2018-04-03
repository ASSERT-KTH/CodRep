import org.jboss.system.ServiceMBeanSupport;

/*
 * JBoss, the OpenSource EJB server
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
package org.jboss.util;

import java.lang.reflect.Constructor;
import java.security.InvalidParameterException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Date;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Map;
import java.util.StringTokenizer;
import java.util.Vector;

import javax.management.MalformedObjectNameException;
import javax.management.MBeanServer;
import javax.management.Notification;
import javax.management.timer.TimerNotification;
import javax.management.NotificationFilter;
import javax.management.NotificationListener;
import javax.management.ObjectName;
import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.Name;
import javax.naming.NamingException;
import javax.naming.NameNotFoundException;
import javax.naming.Reference;
import javax.naming.StringRefAddr;

import org.jboss.logging.Log;
import org.jboss.naming.NonSerializableFactory;
import org.jboss.util.ServiceMBeanSupport;

/**
* Scheduler Instance to allow clients to run this as a
* scheduling service for any Schedulable instances.
*
* @author <a href="mailto:andreas.schaefer@madplanet.com">Andreas Schaefer</a>
* @author Cameron (camtabor)
*
* <p><b>Revisions:</b></p>
* <p><b>20010814 Cameron:</b>
* <ul>
* <li>Checks if the TimerMBean is already loaded</li>
* <li>Created a SchedulerNotificationFilter so that each Scheduler only
*     get its notifications</li>
* <li>Stop was broken because removeNotification( Integer ) was broken</li>
* </ul>
* </p>
**/
public class Scheduler
   extends ServiceMBeanSupport
   implements SchedulerMBean
{

   // -------------------------------------------------------------------------
   // Constants
   // -------------------------------------------------------------------------

   public static String JNDI_NAME = "scheduler:domain";
   public static String JMX_NAME = "scheduler";

   // -------------------------------------------------------------------------
   // Members
   // -------------------------------------------------------------------------

   private String mName;

   private long mActualSchedulePeriod;
   private long mRemainingRepetitions = 0;
   private int mActualSchedule = -1;
   private ObjectName mTimer;
   private Schedulable mSchedulable;

   private boolean mScheduleIsStarted = false;
   private boolean mWaitForNextCallToStop = false;
   private boolean mStartOnStart = false;
   private boolean mIsRestartPending = true;

   // Pending values which can be different to the actual ones
   private Class mSchedulableClass;
   private String mSchedulableArguments;
   private String[] mSchedulableArgumentList = new String[ 0 ];
   private String mSchedulableArgumentTypes;
   private Class[] mSchedulableArgumentTypeList = new Class[ 0 ];
   private Date mStartDate;
   private long mSchedulePeriod;
   private long mInitialRepetitions;

   // -------------------------------------------------------------------------
   // Constructors
   // -------------------------------------------------------------------------

   /**
    * Default (no-args) Constructor
    **/
   public Scheduler()
   {
      mName = null;
   }

   /**
    * Constructor with the necessary attributes to be set
    *
    * @param pName Name of the MBean
    **/
   public Scheduler( String pName )
   {
      mName = pName;
   }

   /**
    * Constructor with the necessary attributes to be set
    *
    * @param pName Name of the MBean
    **/
   public Scheduler(
      String pName,
      String pSchedulableClass,
      String pInitArguments,
      String pInitTypes,
      long pInitialStartDate,
      long pSchedulePeriod,
      long pNumberOfRepetitions
   ) {
      mName = pName;
      mStartOnStart = true;
      setSchedulableClass( pSchedulableClass );
      setSchedulableArguments( pInitArguments );
      setSchedulableArgumentTypes( pInitTypes );
      mStartDate = new Date( pInitialStartDate );
      setSchedulePeriod( pSchedulePeriod );
      setInitialRepetitions( pNumberOfRepetitions );
   }

   // -------------------------------------------------------------------------
   // SchedulerMBean Methods
   // -------------------------------------------------------------------------

   public void startSchedule() {
      // Check if not already started
      if( !isStarted() ) {
         try {
            // Check the given attributes if correct
            if( mSchedulableClass == null ) {
               throw new InvalidParameterException(
                  "Schedulable Class must be set"
               );
            }
            if( mSchedulableArgumentList.length != mSchedulableArgumentTypeList.length ) {
               throw new InvalidParameterException(
                  "Schedulable Class Arguments and Types do not match in length"
               );
            }
            if( mSchedulePeriod <= 0 ) {
               throw new InvalidParameterException(
                  "Schedule Period must be set and greater than 0 (ms)"
               );
            }
            // Create all the Objects for the Constructor to be called
            Object[] lArgumentList = new Object[ mSchedulableArgumentTypeList.length ];
            try {
               for( int i = 0; i < mSchedulableArgumentTypeList.length; i++ ) {
                  Class lClass = mSchedulableArgumentTypeList[ i ];
                  if( lClass == Boolean.TYPE ) {
                     lArgumentList[ i ] = new Boolean( mSchedulableArgumentList[ i ] );
                  } else
                  if( lClass == Integer.TYPE ) {
                     lArgumentList[ i ] = new Integer( mSchedulableArgumentList[ i ] );
                  } else
                  if( lClass == Long.TYPE ) {
                     lArgumentList[ i ] = new Long( mSchedulableArgumentList[ i ] );
                  } else
                  if( lClass == Short.TYPE ) {
                     lArgumentList[ i ] = new Short( mSchedulableArgumentList[ i ] );
                  } else
                  if( lClass == Float.TYPE ) {
                     lArgumentList[ i ] = new Float( mSchedulableArgumentList[ i ] );
                  } else
                  if( lClass == Double.TYPE ) {
                     lArgumentList[ i ] = new Double( mSchedulableArgumentList[ i ] );
                  } else
                  if( lClass == Byte.TYPE ) {
                     lArgumentList[ i ] = new Byte( mSchedulableArgumentList[ i ] );
                  } else
                  if( lClass == Character.TYPE ) {
                     lArgumentList[ i ] = new Character( mSchedulableArgumentList[ i ].charAt( 0 ) );
                  } else {
                     Constructor lConstructor = lClass.getConstructor( new Class[] { String.class } );
                     lArgumentList[ i ] = lConstructor.newInstance( new Object[] { mSchedulableArgumentList[ i ] } );
                  }
               }
            }
            catch( Exception e ) {
               throw new InvalidParameterException( "Could not load or create a constructor argument" );
            }
            try {
               // Check if constructor is found
               Constructor lSchedulableConstructor = mSchedulableClass.getConstructor( mSchedulableArgumentTypeList );
               // Create an instance of it
               mSchedulable = (Schedulable) lSchedulableConstructor.newInstance( lArgumentList );
            }
            catch( Exception e ) {
               throw new InvalidParameterException( "Could not find the constructor or create the Schedulable Instance" );
            }

            mRemainingRepetitions = mInitialRepetitions;
            mActualSchedulePeriod = mSchedulePeriod;
            // Register the Schedule at the Timer
            if( mStartDate == null || mStartDate.getTime() < new Date().getTime() ) {
               mStartDate = new Date( new Date().getTime() + 1000 );
               // Start Schedule now
               System.out.println( "Start regular Schedule with period: " + mActualSchedulePeriod );
               if( mRemainingRepetitions > 0 ) {
                  System.out.println( "Start Schedule wtih " + mRemainingRepetitions + " reps." );
                  mActualSchedule = ( (Integer) getServer().invoke(
                     mTimer,
                     "addNotification",
                     new Object[] {
                        "Schedule",
                        "Scheduler Notification",
                        null,
                        new Date( new Date().getTime() + 1000 ),
                        new Long( mActualSchedulePeriod ),
                        new Long( mRemainingRepetitions )
                     },
                     new String[] {
                        "".getClass().getName(),
                        "".getClass().getName(),
                        Object.class.getName(),
                        Date.class.getName(),
                        Long.TYPE.getName(),
                        Long.TYPE.getName()
                     }
                  ) ).intValue();
               }
               else {
                  System.out.println( "Start Schedule with unlimited reps." );
                  mActualSchedule = ( (Integer) getServer().invoke(
                     mTimer,
                     "addNotification",
                     new Object[] {
                        "Schedule",
                        "Scheduler Notification",
                        null,
                        new Date( new Date().getTime() + 1000 ),
                        new Long( mActualSchedulePeriod )
                     },
                     new String[] {
                        String.class.getName(),
                        String.class.getName(),
                        Object.class.getName(),
                        Date.class.getName(),
                        Long.TYPE.getName()
                     }
                  ) ).intValue();
               }
            }
            else {
               // Add an initial call
               mActualSchedule = ( (Integer) getServer().invoke(
                  mTimer,
                  "addNotification",
                  new Object[] {
                     "Schedule",
                     "Scheduler Notification",
                     mStartDate
                  },
                  new String[] {
                     String.class.getName(),
                     String.class.getName(),
                     Date.class.getName(),
                  }
               ) ).intValue();
            }
            // Register the notificaiton listener at the MBeanServer
            getServer().addNotificationListener(
               mTimer,
               new Listener( mSchedulable ),
               new SchedulerNotificationFilter(new Integer(mActualSchedule)),
               // No object handback necessary
               null
            );
            mScheduleIsStarted = true;
            mIsRestartPending = false;
         }
         catch( Exception e ) {
            e.printStackTrace();
         }
      }
   }

   public void stopSchedule(
      boolean pDoItNow
   ) {
      try {
         if( pDoItNow ) {
            // Remove notification listener now
            mWaitForNextCallToStop = false;
            getServer().invoke(
               mTimer,
               "removeNotification",
               new Object[] {
                  new Integer( mActualSchedule )
               },
               new String[] {
                  "java.lang.Integer" ,
               }
            );
            mActualSchedule = -1;
            mScheduleIsStarted = false;
         }
         else {
            mWaitForNextCallToStop = true;
         }
      }
      catch( Exception e ) {
         e.printStackTrace();
      }
   }

   public void restartSchedule() {
      stopSchedule( true );
      startSchedule();
   }

   public String getSchedulableClass() {
      if( mSchedulableClass == null ) {
         return null;
      }
      return mSchedulableClass.getName();
   }

   public void setSchedulableClass( String pSchedulableClass )
      throws InvalidParameterException
   {
      if( pSchedulableClass == null || pSchedulableClass.equals( "" ) ) {
         throw new InvalidParameterException( "Schedulable Class cannot be empty or undefined" );
      }
      try {
         // Try to load the Schedulable Class
         mSchedulableClass = Thread.currentThread().getContextClassLoader().loadClass( pSchedulableClass );
         // Check if instance of Schedulable
         Class[] lInterfaces = mSchedulableClass.getInterfaces();
         boolean lFound = false;
         for( int i = 0; i < lInterfaces.length; i++ ) {
            if( lInterfaces[ i ] == Schedulable.class ) {
               lFound = true;
               break;
            }
         }
         if( !lFound ) {
            throw new InvalidParameterException(
               "Given class " + pSchedulableClass + " is not instance of Schedulable"
            );
         }
      }
      catch( ClassNotFoundException cnfe ) {
         throw new InvalidParameterException(
            "Given class " + pSchedulableClass + " is not valid or not found"
         );
      }
      mIsRestartPending = true;
   }

   public String getSchedulableArguments() {
      return mSchedulableArguments;
   }

   public void setSchedulableArguments( String pArgumentList ) {
      if( pArgumentList == null || pArgumentList.equals( "" ) ) {
         mSchedulableArgumentList = new String[ 0 ];
      }
      else {
         StringTokenizer lTokenizer = new StringTokenizer( pArgumentList, "," );
         Vector lList = new Vector();
         while( lTokenizer.hasMoreTokens() ) {
            String lToken = lTokenizer.nextToken().trim();
            if( lToken.equals( "" ) ) {
               lList.add( "null" );
            }
            else {
               lList.add( lToken );
            }
         }
         mSchedulableArgumentList = (String[]) lList.toArray( new String[ 0 ] );
      }
      mSchedulableArguments = pArgumentList;
      mIsRestartPending = true;
   }

   public String getSchedulableArgumentTypes() {
      return mSchedulableArgumentTypes;
   }

   public void setSchedulableArgumentTypes( String pTypeList )
      throws InvalidParameterException
   {
      if( pTypeList == null || pTypeList.equals( "" ) ) {
         mSchedulableArgumentTypeList = new Class[ 0 ];
      }
      else {
         StringTokenizer lTokenizer = new StringTokenizer( pTypeList, "," );
         Vector lList = new Vector();
         while( lTokenizer.hasMoreTokens() ) {
            String lToken = lTokenizer.nextToken().trim();
            // Get the class
            Class lClass = null;
            if( lToken.equals( "short" ) ) {
              lClass = Short.TYPE;
            } else
            if( lToken.equals( "int" ) ) {
              lClass = Integer.TYPE;
            } else
            if( lToken.equals( "long" ) ) {
              lClass = Long.TYPE;
            } else
            if( lToken.equals( "byte" ) ) {
              lClass = Byte.TYPE;
            } else
            if( lToken.equals( "char" ) ) {
              lClass = Character.TYPE;
            } else
            if( lToken.equals( "float" ) ) {
              lClass = Float.TYPE;
            } else
            if( lToken.equals( "double" ) ) {
              lClass = Double.TYPE;
            } else
            if( lToken.equals( "boolean" ) ) {
              lClass = Boolean.TYPE;
            }
            if( lClass == null ) {
               try {
                  // Load class to check if available
                  lClass = Thread.currentThread().getContextClassLoader().loadClass( lToken );
               }
               catch( ClassNotFoundException cnfe ) {
                  throw new InvalidParameterException(
                     "The argument type: " + lToken + " is not a valid class or could not be found"
                  );
               }
            }
            lList.add( lClass );
         }
         mSchedulableArgumentTypeList = (Class[]) lList.toArray( new Class[ 0 ] );
      }
      mSchedulableArgumentTypes = pTypeList;
      mIsRestartPending = true;
   }

   public long getSchedulePeriod() {
      return mSchedulePeriod;
   }

   public void setSchedulePeriod( long pPeriod ) {
      if( pPeriod <= 0 ) {
         throw new InvalidParameterException( "Schedulable Period may be not less or equals than 0" );
      }
      mSchedulePeriod = pPeriod;
      mIsRestartPending = true;
   }

   public long getInitialRepetitions() {
      return mInitialRepetitions;
   }

   public void setInitialRepetitions( long pNumberOfCalls ) {
      if( pNumberOfCalls <= 0 ) {
         pNumberOfCalls = -1;
      }
      mInitialRepetitions = pNumberOfCalls;
      mIsRestartPending = true;
   }

   public long getRemainingRepetitions() {
      return mRemainingRepetitions;
   }

   public boolean isStarted() {
      return mScheduleIsStarted;
   }

   public boolean isRestartPending() {
      return mIsRestartPending;
   }

   // -------------------------------------------------------------------------
   // Methods
   // -------------------------------------------------------------------------

   public ObjectName getObjectName(
      MBeanServer pServer,
      ObjectName pName
   )
      throws MalformedObjectNameException
   {
      return pName;
   }

   public String getJNDIName() {
      if( mName != null ) {
         return JMX_NAME + ":" + mName;
      }
      else {
         return JMX_NAME;
      }
   }

   public String getName() {
      return "JBoss Scheduler MBean";
   }

   // -------------------------------------------------------------------------
   // ServiceMBean - Methods
   // -------------------------------------------------------------------------

   protected void initService()
        throws Exception
   {
   }

   protected void startService()
        throws Exception
   {
      bind( this );
      try {
         // Create Timer MBean if need be

           mTimer = new ObjectName( "DefaultDomain", "service", "Timer");
           if ( !getServer().isRegistered(mTimer)){
             getServer().createMBean( "javax.management.timer.Timer", mTimer );
             // Now start the Timer
             getServer().invoke(
                mTimer,
                "start",
                new Object[] {},
                new String[] {}
             );
         }
      }
      catch( Exception e ) {
         e.printStackTrace();
      }
      if( mStartOnStart ) {
         startSchedule();
      }
   }

   protected void stopService() {
      try {
         unbind();
      }
      catch( Exception e ) {
         log.exception( e );
      }
   }

   // -------------------------------------------------------------------------
   // Helper methods to bind/unbind the Management class
   // -------------------------------------------------------------------------

	private void bind( Scheduler pScheduler )
      throws
         NamingException
   {
		Context lContext = new InitialContext();
		String lJNDIName = getJNDIName();

		// Ah ! JBoss Server isn't serializable, so we use a helper class
		NonSerializableFactory.bind( lJNDIName, pScheduler );

      //AS Don't ask me what I am doing here
		Name lName = lContext.getNameParser("").parse( lJNDIName );
		while( lName.size() > 1 ) {
			String lContextName = lName.get( 0 );
			try {
				lContext = (Context) lContext.lookup(lContextName);
			}
			catch( NameNotFoundException e )	{
				lContext = lContext.createSubcontext(lContextName);
			}
			lName = lName.getSuffix( 1 );
		}

		// The helper class NonSerializableFactory uses address type nns, we go on to
		// use the helper class to bind the javax.mail.Session object in JNDI
		StringRefAddr lAddress = new StringRefAddr( "nns", lJNDIName );
		Reference lReference = new Reference(
         Scheduler.class.getName(),
         lAddress,
         NonSerializableFactory.class.getName(),
         null
      );
		lContext.bind( lName.get( 0 ), lReference );

		log.log( "JBoss Scheduler Service '" + getJNDIName() + "' bound to " + lJNDIName );
	}

	private void unbind() throws NamingException {
      String lJNDIName = getJNDIName();

      new InitialContext().unbind( lJNDIName );
      NonSerializableFactory.unbind( lJNDIName );
      log.log("JBoss Scheduler service '" + lJNDIName + "' removed from JNDI" );
	}

   // -------------------------------------------------------------------------
   // Inner Classes
   // -------------------------------------------------------------------------

   public class Listener
      implements NotificationListener
   {

      private Schedulable mDelegate;

      public Listener( Schedulable pDelegate ) {
         mDelegate = pDelegate;
      }

      public void handleNotification(
         Notification pNotification,
         Object pHandback
      ) {
         System.out.println( "Listener.handleNotification(), notification: " + pNotification );
         try {
            // If schedule is started invoke the schedule method on the Schedulable instance
            if( isStarted() ) {
               if( getRemainingRepetitions() > 0 || getRemainingRepetitions() < 0 ) {
                  mDelegate.perform(
                     new Date(),
                     getRemainingRepetitions()
                  );
                  if( mRemainingRepetitions > 0 ) {
                     mRemainingRepetitions--;
                  }
                  if( getRemainingRepetitions() == 0 || mWaitForNextCallToStop ) {
                     stopSchedule( true );
                  }
                  else {
                     if( "InitialCall".equals( pNotification.getType() ) ) {
                        // When Initial Call then setup the regular schedule
                        // By first removing the initial one and then adding the
                        // regular one.
                        getServer().invoke(
                           mTimer,
                           "removeNotification",
                           new Object[] {
                              new Integer( mActualSchedule )
                           },
                           new String[] {
                              "java.lang.Integer",
                           }
                        );
                        // Add regular schedule
                        mActualSchedule = ( (Integer) getServer().invoke(
                           mTimer,
                           "addNotification",
                           new Object[] {
                              "Schedule",
                              "Scheduler Notification",
                              new Date( new Date().getTime() + 1000 ),
                              new Long( mActualSchedulePeriod ),
                              new Long( getRemainingRepetitions() )
                           },
                           new String[] {
                              "".getClass().getName(),
                              "".getClass().getName(),
                              Date.class.getName(),
                              Long.TYPE.getName(),
                              Long.TYPE.getName()
                           }
                        ) ).intValue();
                     }
                  }
               }
            }
            else {
               // Schedule is stopped therefore remove the Schedule
               getServer().invoke(
                  mTimer,
                  "removeNotification",
                  new Object[] {
                     new Integer( mActualSchedule )
                  },
                  new String[] {
                     "java.lang.Integer",
                  }
               );
               mActualSchedule = -1;
            }
         }
         catch( Exception e ) {
            e.printStackTrace();
         }
      }
   }

   /**
    * A test class for a Schedulable Class
    **/
   public static class SchedulableExample
      implements Schedulable
   {

      private String mName;
      private int mValue;

      public SchedulableExample(
         String pName,
         int pValue
      ) {
         mName = pName;
         mValue = pValue;
      }

      /**
       * Just log the call
       **/
      public void perform(
         Date pTimeOfCall,
         long pRemainingRepetitions
      ) {
         System.out.println( "Schedulable Examples is called at: " + pTimeOfCall +
            ", remaining repetitions: " + pRemainingRepetitions +
            ", test, name: " + mName + ", value: " + mValue );
      }
   }
}

/**
 * Filter to ensure that each Scheduler only gets notified when it is supposed to.
 */
class SchedulerNotificationFilter implements javax.management.NotificationFilter{

   private Integer mId;

   /**
    * Create a Filter.
    * @param id the Scheduler id
    */
   public SchedulerNotificationFilter(Integer id){
     mId = id;
   }

   /**
    * Determine if the notification should be sent to this Scheduler
    */
   public boolean isNotificationEnabled(Notification notification){
     if (notification instanceof javax.management.timer.TimerNotification){
       TimerNotification timerNotification = (TimerNotification) notification;
       if (timerNotification.getNotificationID().equals(mId)){
         return true;
       }
     }
     return false;
   }

}