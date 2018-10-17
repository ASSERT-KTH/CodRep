long pRemainingRepetitions

/*
 * JBoss, the OpenSource EJB server
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
package org.jboss.util;

import java.util.Date;

/**
 * This interface defines the manageable interface for a Scheduler Service
 * allowing the client to create a Schedulable instance which is then run
 * by this service at given times.
 *
 * @author Andreas Schaefer (andreas.schaefer@madplanet.com)
 **/
public interface Schedulable
{
   // -------------------------------------------------------------------------
   // Constants
   // -------------------------------------------------------------------------  

   // -------------------------------------------------------------------------
   // Methods
   // -------------------------------------------------------------------------

   /**
    * This method is called from the Scheduler Service
    *
    * @param pTimeOfCall Date/Time of the scheduled call
    * @param pRemainingRepetitions Number of the remaining repetitions which
    *                              is -1 if there is an unlimited number of
    *                              repetitions.
    **/
   public void perform(
      Date pTimeOfCall,
      int pRemainingRepetitions
   );
}