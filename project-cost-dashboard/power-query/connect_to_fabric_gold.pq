// Option A: connect to the Fabric Warehouse Gold layer (production).
// Replace the two parameters with your Fabric SQL endpoint and warehouse name.
// Create one query per table, changing only the [Item] value.

let
    FabricServer    = "your-workspace.datawarehouse.fabric.microsoft.com",
    FabricWarehouse = "main_warehouse",
    Source          = Sql.Database(FabricServer, FabricWarehouse),
    FactProjectCost = Source{[Schema = "gold", Item = "fact_project_cost"]}[Data],
    KeepColumns     = Table.SelectColumns(
                          FactProjectCost,
                          {"expenditure_item_id", "line_num", "gl_date_key", "project_key",
                           "organization_key", "expenditure_type_key", "billable_flag",
                           "quantity", "raw_cost", "burdened_cost"})
in
    KeepColumns


// Option B: load the sample CSV files from this repo (demo / offline).
// Set SampleFolder to where you saved the sample-data folder.

let
    SampleFolder = "C:\portfolio\project-cost-dashboard\sample-data\",
    Source       = Csv.Document(
                       File.Contents(SampleFolder & "fact_project_cost.csv"),
                       [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Headers      = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed        = Table.TransformColumnTypes(
                       Headers,
                       {{"expenditure_item_id", Int64.Type}, {"line_num", Int64.Type},
                        {"gl_date_key", Int64.Type}, {"project_key", Int64.Type},
                        {"organization_key", Int64.Type}, {"expenditure_type_key", Int64.Type},
                        {"billable_flag", type text}, {"quantity", type number},
                        {"raw_cost", Currency.Type}, {"burdened_cost", Currency.Type}})
in
    Typed
