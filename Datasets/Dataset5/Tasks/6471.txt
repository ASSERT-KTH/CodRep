package org.eclipse.xtend.middleend.old;

package org.eclipse.xtend.middleend.old.first;


public class Person {
    private String _name;
    private String _firstName;
    
    public String getName () {
        return _name;
    }
    public void setName (String name) {
        _name = name;
    }
    public String getFirstName () {
        return _firstName;
    }
    public void setFirstName (String firstName) {
        _firstName = firstName;
    }
    
    public String retrieveTheFullName () {
        return _firstName + " " + _name;
    }
    
    public Person getMother () { // to test for endless recursion during type initialization
        return null;
    }
}