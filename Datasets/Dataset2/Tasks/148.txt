static public final boolean debug = false;

//Source file: D:\\tmp\\generated\\s1\\struts\\component\\xmlDefinition\\XmlDefinition.java

package org.apache.struts.tiles.xmlDefinition;

import org.apache.struts.tiles.ComponentDefinition;
import org.apache.struts.tiles.NoSuchDefinitionException;

import java.util.Iterator;

/**
A definition red from an XML definitions file.
*/
public class XmlDefinition extends ComponentDefinition
{
    /** Debug flag */
  static public final boolean debug = true;
  /**
   * Extends attribute value.
   */
  private String inherit;

  /**
   * Use for resolving inheritance.
   */
  private boolean isVisited=false;


     /**
      * Constructor.
      */
   public XmlDefinition()
   {
   super();
   //if(debug)
     //System.out.println( "create definition" );
   }

  /**
   * add an attribute to this component
   *
   * @param attribute Attribute to add.
   */
  public void addAttribute( XmlAttribute attribute)
    {
    putAttribute( attribute.getName(), attribute.getValue() );
    }

  /**
   * Sets the value of the extend and path property.
   *
   * @param aPath the new value of the path property
   */
  public void setExtends(String name)
    {
    inherit = name;
    }

  /**
   * Access method for the path property.
   *
   * @return   the current value of the path property
   */
  public String getExtends()
    {
    return inherit;
    }

  /**
   * Get the value of the extendproperty.
   *
   */
  public boolean isExtending( )
    {
    return inherit!=null;
    }

  /**
   * Get the value of the extendproperty.
   *
   */
  public void setIsVisited( boolean isVisited )
    {
    this.isVisited = isVisited;
    }

    /**
     * Resolve inheritance.
     * First, resolve parent's inheritance, then set path to the parent's path.
     * Also copy attributes setted in parent, and not set in child
     * If instance doesn't extends something, do nothing.
     * @throw NoSuchInstanceException If a inheritance can be solved.
     */
  public void resolveInheritance( XmlDefinitionsSet definitionsSet )
    throws NoSuchDefinitionException
    {
      // Already done, or not needed ?
    if( isVisited || !isExtending() )
      return;

    if( debug)
      System.out.println( "Resolve definition for child name='"
                           + getName()    + "' extends='"
                           + getExtends() + "'." );

      // Set as visited to avoid endless recurisvity.
    setIsVisited( true );

      // Resolve parent before itself.
    XmlDefinition parent = definitionsSet.getDefinition( getExtends() );
    if( parent == null )
      { // error
      String msg = "Error while resolving definition inheritance: child '"
                           + getName() +    "' can't find its ancestor '"
                           + getExtends() + "'. Please check your description file.";
      System.out.println( msg );
        // to do : find better exception
      throw new NoSuchDefinitionException( msg );
      }

    parent.resolveInheritance( definitionsSet );

      // Iterate on each parent's attribute, and add it if not defined in child.
    Iterator parentAttributes = parent.getAttributes().keySet().iterator();
    while( parentAttributes.hasNext() )
      {
      String name = (String)parentAttributes.next();
      if( !getAttributes().containsKey(name) )
        putAttribute( name, parent.getAttribute(name) );
      }
      // Set path
    setPath( parent.getPath() );
    }

  /**
   * Overload this definition with passed child.
   * All attributes from child are copied to this definition. Previous attribute with
   * same name are disguarded.
   * Special attribute 'path','role' and 'extends' are overloaded if defined in child.
   * @param child Child used to overload this definition.
   */
  public void overload( XmlDefinition child )
    {
    if( child.getPath() != null )
      {
      path = child.getPath();
      }
    if( child.getExtends() != null )
      {
      inherit = child.getExtends();
      }
    if( child.getRole() != null )
      {
      role = child.getRole();
      }
      // put all child attributes in parent.
    attributes.putAll( child.getAttributes());
    }
}