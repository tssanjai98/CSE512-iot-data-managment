from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import DCAwareRoundRobinPolicy
from dataclasses import dataclass
from cassandra.query import SimpleStatement
from typing import List, Dict, Optional
import json
import uuid
from datetime import datetime, date


@dataclass
class QueryNode:
    node_id: str
    operation: str
    details: Dict
    children: List["QueryNode"] = None
    metrics: Dict = None


class CassandraQueryVisualizer:
    def __init__(self, trace_data: Dict):
        self.trace_data = trace_data
        self.root_node = None

    def build_tree(self) -> QueryNode:
        """Build a tree structure from trace events"""
        events = sorted(self.trace_data["events"], key=lambda x: x["source_elapsed"])
        root_id = str(uuid.uuid4())

        self.root_node = QueryNode(
            node_id=root_id,
            operation="Query Execution",
            details={"coordinator": self.trace_data["coordinator"]},
            children=[],
            metrics={
                "duration": self.trace_data["duration"],
                "total_events": len(events),
            },
        )

        current_node = self.root_node
        for event in events:
            node = QueryNode(
                node_id=str(uuid.uuid4()),
                # operation=self._classify_operation(event["activity"]),
                operation=event["activity"],
                details={
                    "activity": event["activity"],
                    "source": event["source"],
                    "elapsed": event["source_elapsed"],
                },
                children=[],
                metrics={"elapsed_time": event["source_elapsed"]},
            )
            current_node.children.append(node)

        return self.root_node

    def _classify_operation(self, activity: str) -> str:
        """Classify trace activity into operation types"""
        activity = activity.lower()
        if "partition" in activity:
            return "Partition Read"
        elif "scan" in activity:
            return "Table Scan"
        elif "read" in activity:
            return "Read Operation"
        elif "write" in activity:
            return "Write Operation"
        elif "filter" in activity:
            return "Filter Operation"
        else:
            return "Other Operation"

    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram from query tree"""
        if not self.root_node:
            self.build_tree()

        mermaid_lines = ["graph TD"]

        def add_node(node: QueryNode, parent_id: Optional[str] = None):
            # Replace <br/> with \n for Mermaid compatibility
            node_label = f"{node.operation}\n{self._format_metrics(node.metrics)}"
            node_id = node.node_id.replace("-", "_")  # Replace dashes for Mermaid compatibility
            mermaid_lines.append(f'{node_id}["{node_label}"]')

            if parent_id:
                parent_id = parent_id.replace("-", "_")
                mermaid_lines.append(f"{parent_id} --> {node_id}")

            if node.children:
                for child in node.children:
                    add_node(child, node.node_id)

        add_node(self.root_node)
        return "\n".join(mermaid_lines)


    def _get_node_style(self, operation: str) -> str:
        """Get Mermaid node style based on operation type"""
        styles = {
            "Query Execution": ":::queryRoot",
            "Partition Read": ":::partition",
            "Table Scan": ":::scan",
            "Read Operation": ":::read",
            "Write Operation": ":::write",
            "Filter Operation": ":::filter",
            "Other Operation": ":::other",
        }
        return styles.get(operation, "")

    def _format_metrics(self, metrics: Dict) -> str:
        """Format metrics for display in node"""
        if not metrics:
            return ""

        formatted = []
        for key, value in metrics.items():
            formatted.append(f"{key}: {value}")
        return "\n".join(formatted)


# class EnhancedCassandraQueryOptimizer:
#     def __init__(self, contact_points=['localhost'], keyspace='kafka_data'):
#         # Previous initialization code remains the same...
#         self.visualizer = None
#         self.mermaid_diagrams = []

#     def analyze_query(self, query: str, parameters: Dict = None) -> Dict:
#         """Analyze query and generate visual representation"""
#         # Execute query with tracing
#         statement = SimpleStatement(query)
#         statement.trace = True

#         result = self.session.execute(statement, parameters or {})
#         trace = result.get_query_trace()

#         # Create visualizer and generate diagram
#         self.visualizer = CassandraQueryVisualizer(self._process_trace(trace))
#         mermaid_diagram = self.visualizer.generate_mermaid()
#         self.mermaid_diagrams.append(mermaid_diagram)

#         return {
#             'trace': trace,
#             'mermaid_diagram': mermaid_diagram,
#             'metrics': {
#                 'duration': trace.duration,
#                 'coordinator': trace.coordinator,
#                 'events_count': len(trace.events)
#             }
#         }


class EnhancedCassandraQueryOptimizer:
    def __init__(self, contact_points=["localhost"], keyspace="iot_data_management", port=9042):
        """
        Initialize Cassandra connection with configurable contact points and keyspace

        Args:
            contact_points (List[str]): List of Cassandra server addresses
            keyspace (str): Cassandra keyspace to connect to
            port (int): Cassandra server port
        """
        # Configure execution profile
        profile = ExecutionProfile(
            load_balancing_policy=DCAwareRoundRobinPolicy(),
            # Add more configuration options as needed
        )

        # Create Cassandra cluster connection
        self.cluster = Cluster(
            contact_points=contact_points,
            port=port,
            execution_profiles={EXEC_PROFILE_DEFAULT: profile},
        )

        try:
            # Establish session and connect to keyspace
            self.session = self.cluster.connect(keyspace)
            print(f"Connected to Cassandra cluster at {contact_points}")
        except Exception as e:
            print(f"Error connecting to Cassandra: {e}")
            raise

        self.visualizer = None
        self.mermaid_diagrams = []

    def _process_trace(self, trace):
        """
        Process query trace into a dictionary format

        Args:
            trace: Cassandra query trace object

        Returns:
            Dict: Processed trace information
        """
        return {
            "coordinator": str(trace.coordinator),
            "duration": trace.duration,
            "events": [
                {
                    "activity": event.description,
                    "source": str(event.source),
                    "source_elapsed": event.source_elapsed,
                }
                for event in trace.events
            ],
        }

    def analyze_query(self, query: str, parameters: Dict = None) -> Dict:
        """
        Analyze query and generate visual representation

        Args:
            query (str): CQL query to execute
            parameters (Dict, optional): Query parameters

        Returns:
            Dict: Analysis results including trace and Mermaid diagram
        """
        try:
            # Execute query with tracing
            statement = SimpleStatement(query)
            statement.trace = True

            result = self.session.execute(statement, parameters or {},trace=True)
            print(result)
            res=[]
            for row in result:
                    # print(row._asdict())
                    res.append(row._asdict())
            trace = result.get_query_trace()

            # Create visualizer and generate diagram
            self.visualizer = CassandraQueryVisualizer(self._process_trace(trace))
            mermaid_diagram = self.visualizer.generate_mermaid()
            self.mermaid_diagrams.append(mermaid_diagram)

            return {
                "trace": trace,
                "mermaid_diagram": mermaid_diagram,
                "metrics": {
                    "duration": trace.duration,
                    "coordinator": str(trace.coordinator),
                    "events_count": len(trace.events),
                },
                "query_result":res
            }
        except Exception as e:
            print(f"Error analyzing query: {e}")
            raise

    def close(self):
        """
        Properly close Cassandra cluster connection
        """
        if self.cluster:
            self.cluster.shutdown()


# def main():
#     # Example usage
#     optimizer = EnhancedCassandraQueryOptimizer(['localhost'])

#     # Example queries to analyze
#     queries = [
#         """
#         SELECT * FROM messages
#         WHERE topic = ? AND date = ?
#         AND timestamp >= ?
#         LIMIT 100
#         """,
#         """
#         SELECT topic, COUNT(*)
#         FROM messages
#         WHERE date = ?
#         GROUP BY topic ALLOW FILTERING
#         """
#     ]

#     # Generate and display query plans
#     for i, query in enumerate(queries, 1):
#         print(f"\nAnalyzing Query {i}:")
#         print(query)

#         analysis = optimizer.analyze_query(query)

#         # Display Mermaid diagram
#         print("\nQuery Plan Visualization:")


# def query_example():
#     optimizer = EnhancedCassandraQueryOptimizer(["localhost"])

#     # Example query with properly formatted parameters
#     query = """
#     SELECT * FROM messages 
#     WHERE topic = %s AND date = %s
#     AND timestamp >=%s
#     LIMIT 100
#     """

#     # Format parameters properly
#     # parameters = ["user_activity", date(2024, 1, 1), datetime(2023, 1, 1, 0, 0, 0)]
#     parameters = ["user_activity", "2024-01-01",  "2024-01-01"]


#     try:
#         analysis = optimizer.analyze_query(query, parameters)
#         print("\nQuery Plan Visualization:")
#         print(analysis["mermaid_diagram"])
#     finally:
#         optimizer.close()


# if __name__ == "__main__":
#     query_example()