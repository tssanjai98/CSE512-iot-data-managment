export const staticApiResponse = {
    query: "SELECT device_id, category, status, battery_level FROM devices WHERE alerts = true",
    searchResults: [
        { device_id: "device_1", category: "sensor", status: "active", battery_level: 78.5 },
        { device_id: "device_2", category: "actuator", status: "maintenance", battery_level: 55.2 },
        { device_id: "device_3", category: "communication", status: "error", battery_level: 33.8 },
    ],
    executionPlans: [
        {
            id: 1,
            description: "Plan 1: Index Scan on Devices Table",
            graph: `classDiagram
            Class01 <|-- AveryLongClass : Cool
            <<Interface>> Class01
            Class09 --> C2 : Where am I?
            Class09 --* C3
            Class09 --|> Class07
            Class07 : equals()
            Class07 : Object[] elementData
            Class01 : size()
            Class01 : int chimp
            Class01 : int gorilla
            class Class10 {
              <<service>>
              int id
              size()
            }`,
        },
        {
            id: 2,
            description: "Plan 2: Sequential Scan with Filter",
            graph: `
            graph TD
            Query --> Seq-Scan-devices-WITH-FILTER
            Seq-Scan-devices-WITH-FILTER --> Group-By-status
            Group-By-status --> Sort-battery-level
            `,
        },
        {
            id: 3,
            description: "Plan 3: Hash Join on Devices and Alerts",
            graph: `
            graph TD
            Query --> Seq-Scan-devices-INDEX-SCAN
            Query --> Seq-Scan-alerts-INDEX-SCAN
            Seq-Scan-devices-INDEX-SCAN --> Hash-Join-devices-alerts
            Seq-Scan-alerts-INDEX-SCAN --> Hash-Join-devices-alerts
            Hash-Join-devices-alerts --> Group-By-status-category
            Group-By-status-category --> Sort-battery-level
            `,
        },
        {
            id: 4,
            description: "Plan 4: Merge Join with Index Scan",
            graph: `
            graph TD
            Query --> Seq-Scan-devices-INDEX-SCAN
            Seq-Scan-devices-INDEX-SCAN --> Merge-Join-devices-alerts
            Merge-Join-devices-alerts --> Group-By-status-category
            Group-By-status-category --> Sort-battery-level
            `,
        },
        {
            id: 5,
            description: "Plan 5: Nested Loop Join with Sequential Scan",
            graph: `
            graph TD
            Query --> Seq-Scan-devices-INDEX-SCAN
            Seq-Scan-devices-INDEX-SCAN --> Nested-Loop-devices-alerts
            Nested-Loop-devices-alerts --> Group-By-status-category
            Group-By-status-category --> Sort-battery-level
            `,
        },
    ],
    selectedPlan: 3, // Chosen plan ID
};
