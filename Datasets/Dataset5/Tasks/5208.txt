public Collection getResults();

/*******************************************************************************
 * Copyright (c) 2008 Marcelo Mayworm. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: 	Marcelo Mayworm - initial API and implementation
 *
 ******************************************************************************/

package org.eclipse.ecf.presence.search;

import java.util.Collection;
import org.eclipse.core.runtime.IAdaptable;

/**
 * This interface provides methods to handle the result list that match the search.
 * @since 2.0
 */
public interface IResultList extends IAdaptable {

	/**
	 * Get results that match the search. Instances of list are of type
	 * {@link IResult}
	 * 
	 * @return Collection of IResult. Will not return <code>null</code>.
	 *         May return an empty Collection.
	 */
	public Collection geResults();

	/**
	 * Get the result that math the specific field and value
	 * @param field field's name used as argument to try to match the search
	 * @param value value for the respective field used as argument to try to match the search
	 * @return IResult will be null case it doesn't exist
	 */
	public IResult getResult(String field, String value);
}