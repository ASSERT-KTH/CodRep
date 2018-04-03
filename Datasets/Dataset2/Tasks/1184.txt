public List executeQuery(List params) throws PersistenceException;

package org.jboss.cmp.schema;

import java.util.List;

public interface QueryCommand
{
   public List executeQuery(List params);
}