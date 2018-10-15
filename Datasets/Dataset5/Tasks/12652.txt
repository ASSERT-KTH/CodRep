package org.eclipse.xtend.backend.testhelpers;

package org.eclipse.xtend.backend.helpers;


public class CounterFunction {
    private int _counter = 0;
    
    public int nextCounterValue () {
        return _counter++;
    }
}