use common_daft_config::PyDaftPlanningConfig;
use daft_dsl::python::PyExpr;
use daft_plan::{LogicalPlanBuilder, PyLogicalPlanBuilder};
use pyo3::prelude::*;

use crate::{catalog::SQLCatalog, planner::SQLPlanner};

#[pyfunction]
pub fn sql(
    sql: &str,
    catalog: PyCatalog,
    daft_planning_config: PyDaftPlanningConfig,
) -> PyResult<PyLogicalPlanBuilder> {
    let mut planner = SQLPlanner::new(catalog.catalog);
    let plan = planner.plan_sql(sql)?;
    Ok(LogicalPlanBuilder::new(plan, Some(daft_planning_config.config)).into())
}

#[pyfunction]
pub fn sql_expr(sql: &str) -> PyResult<PyExpr> {
    let expr = crate::planner::sql_expr(sql)?;
    Ok(PyExpr { expr })
}

/// PyCatalog is the Python interface to the Catalog.
#[pyclass(module = "daft.daft")]
#[derive(Debug, Clone)]
pub struct PyCatalog {
    catalog: SQLCatalog,
}

#[pymethods]
impl PyCatalog {
    /// Construct an empty PyCatalog.
    #[staticmethod]
    pub fn new() -> Self {
        PyCatalog {
            catalog: SQLCatalog::new(),
        }
    }

    /// Register a table with the catalog.
    pub fn register_table(&mut self, name: &str, dataframe: &mut PyLogicalPlanBuilder) {
        let plan = dataframe.builder.build();
        self.catalog.register_table(name, plan);
    }

    /// Copy from another catalog, using tables from other in case of conflict
    pub fn copy_from(&mut self, other: &PyCatalog) {
        self.catalog.copy_from(&other.catalog);
    }

    /// __str__ to print the catalog's tables
    fn __str__(&self) -> String {
        format!("{:?}", self.catalog)
    }
}

impl Default for PyCatalog {
    fn default() -> Self {
        Self::new()
    }
}
