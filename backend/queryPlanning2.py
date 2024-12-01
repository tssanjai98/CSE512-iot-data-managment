import sqlparse
import re


class QueryPlan:
    def __init__(self, graph_code, cost):
        self.graph_code = graph_code
        self.cost = cost

    def __repr__(self):
        return f"Plan with cost {self.cost}:\n{self.graph_code}"


class StreamOptimizer:
    def __init__(self):
        self.plans = []

    def parse_query(self, query):
        """
        Parses the SQL query into its main clauses.
        """
        parsed = sqlparse.parse(query)[0]
        clauses = {"SELECT": [], "FROM": [], "WHERE": [], "ORDER BY": [], "GROUP BY": [], "WINDOW": []}
        current_clause = None

        for token in parsed.tokens:
            if token.ttype is sqlparse.tokens.Keyword and token.value.upper() in clauses:
                current_clause = token.value.upper()
            elif current_clause:
                clauses[current_clause].append(str(token).strip())

        for clause in clauses:
            clauses[clause] = " ".join(clauses[clause]).strip()

        # Handle JOINs in the FROM clause
        from_clause = clauses["FROM"]
        if "JOIN" in from_clause.upper():
            tables = re.split(r"JOIN|ON", from_clause, flags=re.IGNORECASE)
            clauses["FROM"] = [t.strip() for t in tables if t.strip() and "ON" not in t.upper()]
        else:
            clauses["FROM"] = [from_clause]

        return clauses

    def sanitize_mermaid_label(self, label):
        """
        Replaces special characters in labels with meaningful alternatives for Mermaid.
        """
        replacements = {
            ">": "GT",
            "<": "LT",
            "=": "EQ",
            ">=": "GTE",
            "<=": "LTE",
            "!=": "NEQ",
            " ": "_",
            ",": "_",
            "'": "",
            ".": "_",
            "(": "",
            ")": "",
        }
        for symbol, replacement in replacements.items():
            label = label.replace(symbol, replacement)
        return label

    def generate_mermaid_graph(self, parsed_query, scan_types):
        """
        Generates a Mermaid graph code for the query tree with IoT-specific optimizations.
        """
        graph_code = "graph TD\n"
        root = "Query"

        # Add FROM clause with scans
        branch_nodes = []
        for i, table in enumerate(parsed_query["FROM"]):
            scan_type = scan_types[i]
            table_node = f"{scan_type}_{self.sanitize_mermaid_label(table)}"
            graph_code += f"{root} --> {table_node}\n"
            branch_nodes.append(table_node)

        # Handle JOINs
        if len(branch_nodes) > 1:
            join_node = "Join_Devices_Locations_Metrics"
            for node in branch_nodes:
                graph_code += f"{node} --> {join_node}\n"
            last_node = join_node
        else:
            last_node = branch_nodes[0]

        # Add WINDOW aggregation if present
        if parsed_query["WINDOW"]:
            window_node = f"Window_{self.sanitize_mermaid_label(parsed_query['WINDOW'])}"
            graph_code += f"{last_node} --> {window_node}\n"
            last_node = window_node

        # Add WHERE filtering
        if parsed_query["WHERE"]:
            where_node = f"Filter_{self.sanitize_mermaid_label(parsed_query['WHERE'])}"
            graph_code += f"{last_node} --> {where_node}\n"
            last_node = where_node

        # Add GROUP BY
        if parsed_query["GROUP BY"]:
            group_by_node = f"Group_By_{self.sanitize_mermaid_label(parsed_query['GROUP BY'])}"
            graph_code += f"{last_node} --> {group_by_node}\n"
            last_node = group_by_node

        # Add ORDER BY
        if parsed_query["ORDER BY"]:
            order_by_node = f"Sort_{self.sanitize_mermaid_label(parsed_query['ORDER BY'])}"
            graph_code += f"{last_node} --> {order_by_node}\n"
            last_node = order_by_node

        # Add SELECT projection
        if parsed_query["SELECT"]:
            select_node = f"Select_{self.sanitize_mermaid_label(parsed_query['SELECT'])}"
            graph_code += f"{last_node} --> {select_node}\n"

        return graph_code

    def calculate_cost(self, graph_code):
        """
        Calculates cost dynamically based on graph structure.
        """
        cost = 0
        for line in graph_code.splitlines():
            if "Seq_Scan" in line:
                cost += 50  # Sequential scan cost
            elif "Index_Scan" in line:
                cost += 30  # Lower cost for index scans
            elif "Join" in line:
                cost += 100  # Join operation cost
            elif "Window" in line:
                cost += 50  # Windowing cost
            elif "Filter" in line:
                cost += 20  # Filtering cost
            elif "Group_By" in line:
                cost += 40  # Grouping cost
            elif "Sort" in line:
                cost += 25  # Sorting cost
            elif "Select" in line:
                cost += 10  # Projection cost
        return cost

    def generate_plans(self, query):
        """
        Generates multiple query plans dynamically for real-time streaming queries.
        """
        parsed_query = self.parse_query(query)

        # Dynamically adjust scan types based on the number of tables
        num_tables = len(parsed_query["FROM"])
        scan_types_list = [
            ["Seq_Scan"] * num_tables,
            ["Index_Scan"] * num_tables,
            ["Seq_Scan" if i == num_tables - 1 else "Index_Scan" for i in range(num_tables)],
        ]

        for scan_types in scan_types_list:
            graph_code = self.generate_mermaid_graph(parsed_query, scan_types)
            cost = self.calculate_cost(graph_code)
            self.plans.append(QueryPlan(graph_code, cost))

    def pick_best_plan(self):
        """
        Selects the plan with the lowest cost.
        """
        if not self.plans:
            return None
        return min(self.plans, key=lambda plan: plan.cost)


# Example Usage
# if __name__ == "__main__":
#     optimizer = StreamOptimizer()
#     query = """
#     SELECT d.device_id, 
#            l.location_name, 
#            AVG(m.temperature) AS avg_temp, 
#            MAX(m.humidity) AS max_humidity 
#     FROM devices d 
#     JOIN locations l ON d.location_id = l.location_id 
#     JOIN metrics m ON d.device_id = m.device_id 
#     WHERE m.timestamp >= '2024-01-01' 
#     WINDOW SLIDING (15 MINUTES) 
#     GROUP BY d.device_id, l.location_name 
#     ORDER BY avg_temp DESC;
#     """

#     optimizer.generate_plans(query)

#     print("Generated Query Plans:")
#     for plan in optimizer.plans:
#         print(plan)

#     best_plan = optimizer.pick_best_plan()
#     print("\nBest Plan Selected:")
#     print(best_plan)
