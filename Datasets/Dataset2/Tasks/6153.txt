@author <a href="mailto:Scott_Stark@displayscape.com">Scott Stark</a>.

/*
 * JBoss, the OpenSource EJB server
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */

package org.jboss.security;

import java.security.Principal;

/** A simple String based implementation of Principal. Typically
a SimplePrincipal is created given a userID which is used
as the Principal name.

@author <a href="on@ibis.odessa.ua">Oleg Nitz</a>
@author Scott_Stark@displayscape.com
*/
public class SimplePrincipal implements Principal, java.io.Serializable
{
  private String name;

  public SimplePrincipal(String name)
  {
    this.name = name;
  }

  /** Compare this SimplePrincipal's name against another SimplePrincipal
      name or null if this.getName() is null.
  @return true if name == another == null || name equals
      another.toString();
   */
  public boolean equals(Object another)
  {
    if (name == null)
      return (another == null);  
    if ((another == null) || !(another instanceof SimplePrincipal))
      return false;
    return name.equals( another.toString() );
  }

  public int hashCode()
  {
    return (name == null ? 0 : name.hashCode());
  }

  public String toString()
  {
    return name;
  }

  public String getName()
  {
    return name;
  }
} 