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
            graph: `
            graph TD
            Query --> Seq-Scan-devices-INDEX-SCAN
            Seq-Scan-devices-INDEX-SCAN --> Group-By-status-category
            Group-By-status-category --> Sort-battery-level
            `,
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
Query --> Seq_Scan_countries_INDEX_SCAN
Query --> Seq_Scan_regi_INDEX_SCAN
Query --> Seq_Scan_s_INDEX_SCAN
Query --> Seq_Scan_countries_regi_INDEX_SCAN
Query --> Seq_Scan__id_EQ_regi_INDEX_SCAN
Query --> Seq_Scan_s_id_INDEX_SCAN
Query --> Seq_Scan_cities_INDEX_SCAN
Query --> Seq_Scan_regi_INDEX_SCAN
Query --> Seq_Scan_s_city_id_EQ_cities_id______WHERE_year_GT_2010_INDEX_SCAN
Seq_Scan_countries_INDEX_SCAN --> Join_regi_INDEX_SCAN
Seq_Scan_regi_INDEX_SCAN --> Join_s_INDEX_SCAN
Seq_Scan_s_INDEX_SCAN --> Join_countries_regi_INDEX_SCAN
Seq_Scan_countries_regi_INDEX_SCAN --> Join__id_EQ_regi_INDEX_SCAN
Seq_Scan__id_EQ_regi_INDEX_SCAN --> Join_s_id_INDEX_SCAN
Seq_Scan_s_id_INDEX_SCAN --> Join_cities_INDEX_SCAN
Seq_Scan_cities_INDEX_SCAN --> Join_regi_INDEX_SCAN
Seq_Scan_regi_INDEX_SCAN --> Join_s_city_id_EQ_cities_id______WHERE_year_GT_2010_INDEX_SCAN
Join_regi_INDEX_SCAN --> Group_By_year__countryname
Join_s_INDEX_SCAN --> Group_By_year__countryname
Join_countries_regi_INDEX_SCAN --> Group_By_year__countryname
Join__id_EQ_regi_INDEX_SCAN --> Group_By_year__countryname
Join_s_id_INDEX_SCAN --> Group_By_year__countryname
Join_cities_INDEX_SCAN --> Group_By_year__countryname
Join_regi_INDEX_SCAN --> Group_By_year__countryname
Join_s_city_id_EQ_cities_id______WHERE_year_GT_2010_INDEX_SCAN --> Group_By_year__countryname
Seq_Scan_s_city_id_EQ_cities_id______WHERE_year_GT_2010_INDEX_
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
