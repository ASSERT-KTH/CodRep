public static final String OBJECT_NAME = "jboss:service=Scheduler";

/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
package org.jboss.util;

import java.security.InvalidParameterException;
import java.util.Date;

import org.jboss.system.ServiceMBean;

/**
 * This interface defines the manageable interface for a Scheduler Service
 * allowing the client to create a Schedulable instance which is then run
 * by this service at given times.
 *
 * @author <a href="mailto:andreas.schaefer@madplanet.com">Andreas Schaefer</a>
 **/
public interface SchedulerMBean
   extends ServiceMBean
{
   // -------------------------------------------------------------------------
   // Constants
   // -------------------------------------------------------------------------  

   public static final String OBJECT_NAME = "JBOSS-SYSTEM:service=Scheduler";

   // -------------------------------------------------------------------------
   // Methods
   // -------------------------------------------------------------------------

   /**
    * Starts the schedule if the schedule is stopped otherwise nothing will happen.
    * The Schedule is immediately set to started even the first call is in the
    * future.
    *
    * @throws InvalidParameterException If any of the necessary values are not set
    *                                   or invalid (especially for the Schedulable
    *                                   class attributes).
    **/
   public void startSchedule();
   
   /**
    * Stops the schedule because it is either not used anymore or to restart it with
    * new values.
    *
    * @param pDoItNow If true the schedule will be stopped without waiting for the next
    *                 scheduled call otherwise the next call will be performed before
    *                 the schedule is stopped.
    **/
   public void stopSchedule(
      boolean pDoItNow
   );
   
   /**
    * Stops the server right now and starts it right now.
    **/
   public void restartSchedule();
   
   /**
    * @return Full qualified Class name of the schedulable class called by the schedule or
    *         null if not set.
    **/
   public String getSchedulableClass();
   
   /**
    * Sets the fully qualified Class name of the Schedulable Class being called by the
    * Scheduler. Must be set before the Schedule is started. Please also set the
    * {@link #setSchedulableArguments} and {@link #setSchedulableArgumentTypes}.
    *
    * @param pSchedulableClass Fully Qualified Schedulable Class.
    *
    * @throws InvalidParameterException If the given value is not a valid class or cannot
    *                                   be loaded by the Scheduler or is not of instance
    *                                   Schedulable.
    **/
   public void setSchedulableClass( String pSchedulableClass )
      throws InvalidParameterException;
   
   /**
    * @return Comma seperated list of Constructor Arguments used to instantiate the
    *         Schedulable class instance. Right now only basic data types, String and
    *         Classes with a Constructor with a String as only argument are supported.
    **/
   public String getSchedulableArguments();
   
   /**
    * Sets the comma seperated list of arguments for the Schedulable class. Note that
    * this list must have as many elements as the Schedulable Argument Type list otherwise
    * the start of the Scheduler will fail. Right now only basic data types, String and
    * Classes with a Constructor with a String as only argument are supported.
    *
    * @param pArgumentList List of arguments used to create the Schedulable intance. If
    *                      the list is null or empty then the no-args constructor is used.
    **/
   public void setSchedulableArguments( String pArgumentList );
   
   /**
    * @return A comma seperated list of Argument Types which should match the list of
    *         arguments.
    **/
   public String getSchedulableArgumentTypes();
   
   /**
    * Sets the comma seperated list of argument types for the Schedulable class. This will
    * be used to find the right constructor and to created the right instances to call the
    * constructor with. This list must have as many elements as the Schedulable Arguments
    * list otherwise the start of the Scheduler will fail. Right now only basic data types,
    * String and Classes with a Constructor with a String as only argument are supported.
    *
    * @param pTypeList List of arguments used to create the Schedulable intance. If
    *                  the list is null or empty then the no-args constructor is used.
    *
    * @throws InvalidParameterException If the given list contains a unknow datat type.
    **/
   public void setSchedulableArgumentTypes( String pTypeList )
      throws InvalidParameterException;
   
   /**
    * @return Schedule Period between two scheduled calls in Milliseconds. It will always
    *         be bigger than 0 except it returns -1 then the schedule is stopped.
    **/
   public long getSchedulePeriod();
   
   /**
    * Sets the Schedule Period between two scheduled call.
    *
    * @param pPeriod Time between to scheduled calls (after the initial call) in Milliseconds.
    *                This value must be bigger than 0.
    *
    * @throws InvalidParameterException If the given value is less or equal than 0
    **/
   public void setSchedulePeriod( long pPeriod );
   
   /**
   * @return Date (and time) of the first scheduled call. Value is in milliseconds since 1/1/1970.
   *         If date is in the past when the schedule is added to the Timer then the schedule will
   *         started immediately
   **/
   public long getInitialStartDate();
   
   /**
   * Sets the first scheduled call. If in the past when the scheduler gets setup it will start
   * immediately.
   *
   * @param pStartDate Date in milliseconds since 1/1/1970 for the first initial call. Anything
   *                   less than zero means 1/1/1970. Any date less than now means the schedule
   *                   will be started immediately.
   **/
   public void setInitialStartDate( long pStartDate );
   
   /**
    * @return Number of scheduled calls initially. If -1 then there is not limit.
    **/
   public long getInitialRepetitions();
   
   /**
    * Sets the initial number of scheduled calls.
    *
    * @param pNumberOfCalls Initial Number of scheduled calls. If -1 then the number
    *                       is unlimted.
    *
    * @throws InvalidParameterException If the given value is less or equal than 0
    **/
   public void setInitialRepetitions( long pNumberOfCalls );

   /**
    * @return Number of remaining repetitions. If -1 then there is no limit.
    **/
   public long getRemainingRepetitions();
   
   /**
    * @return True if the schedule is up and running. If you want to start the schedule
    *         with another values by using {@ #startSchedule} you have to stop the schedule
    *         first with {@ #stopSchedule} and wait until this method returns false.
    **/
   public boolean isStarted();
   
   /**
    * @return True if any attributes are changed but the Schedule is not restarted yet.
    **/
   public boolean isRestartPending();
   
   /**
   * Set the scheduler to start when MBean started or not. Note that this method only
   * affects when the {@link #startService startService()} gets called (normally at
   * startup time.
   *
   * @param pStartAtStartup True if Schedule has to be started at startup time
   **/
   public void setStartAtStartup( boolean pStartAtStartup );

}