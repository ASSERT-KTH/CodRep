package backtype.storm.metric.api;

package backtype.storm.metric;

public interface IMetric {
    public Object getValueAndReset();
}