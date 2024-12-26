from pyspark.sql import SparkSession

def process_data():
    spark = SparkSession.builder.appName("GCPDataprocJob").getOrCreate()

    # Define your GCP bucket and paths
    bucket = "airflow_projects_repo"
    emp_data_path = f"gs://{bucket}/airflow-project-1/data/employee.csv"
    dept_data_path = f"gs://{bucket}/airflow-project-1/data/department.csv"
    output_path = f"gs://{bucket}/airflow-project-1/output"

    # Read datasets
    employee = spark.read.csv(emp_data_path,header=True,inferSchema=True)
    department = spark.read.csv(dept_data_path,header=True,inferSchema=True)

    # Filter employee data
    filtered_employee = employee.filter(employee.salary>50000)

    # Join datasets
    joined_data = filtered_employee.join(department, "dept_id","inner")

    # Write Output
    joined_data.write.csv(output_path,mode="overwrite",header=True)

    spark.stop()

if __name__ == "main":
    process_data()