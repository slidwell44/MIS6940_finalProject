# Stateless Processing

Stateless stream processing involves operations where each incoming event is processed independently of any other
events. Examples include:

* **Filtering**: Removing messages based on certain criteria.
* **Mapping**: Transforming messages from one format to another.
* **Simple Aggregations**: Counting occurrences without maintaining a history.

# Stateful Processing

Stateful stream processing, on the other hand, maintains state across events. This is essential for:

* **Joins**: Combining streams based on keys.
* **Windowed Aggregations**: Calculating metrics over time windows (e.g., average temperature over an hour).
* **Complex Aggregations**: Maintaining counts, sums, or other metrics that require historical data.