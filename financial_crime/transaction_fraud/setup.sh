gsql -p "graphtiger" /home/tigergraph/solution_kits/financial_crime/library/schema/general_global_financial_crime_super_schema.gsql
gsql -p "graphtiger" /home/tigergraph/solution_kits/financial_crime/transaction_fraud/schema/create_schema_bottomup.gsql

gsql -p "graphtiger" 2_load_data.gsql
. 3_install_queries.sh
