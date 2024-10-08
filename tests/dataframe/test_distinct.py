from __future__ import annotations

import pyarrow as pa
import pytest

from daft import context
from daft.datatype import DataType
from tests.utils import sort_arrow_table

pytestmark = pytest.mark.skipif(
    context.get_context().daft_execution_config.enable_native_executor is True,
    reason="Native executor fails for these tests",
)


@pytest.mark.parametrize("repartition_nparts", [1, 2, 5])
def test_distinct_with_nulls(make_df, repartition_nparts):
    daft_df = make_df(
        {
            "id": [1, None, None, None],
            "values": ["a1", "b1", "b1", "c1"],
        },
        repartition=repartition_nparts,
    )
    daft_df = daft_df.distinct()

    expected = {
        "id": [1, None, None],
        "values": ["a1", "b1", "c1"],
    }
    assert sort_arrow_table(pa.Table.from_pydict(daft_df.to_pydict()), "values") == sort_arrow_table(
        pa.Table.from_pydict(expected), "values"
    )


@pytest.mark.parametrize("repartition_nparts", [1, 2, 5])
def test_distinct_with_all_nulls(make_df, repartition_nparts):
    daft_df = make_df(
        {
            "id": [None, None, None, None],
            "values": ["a1", "b1", "b1", "c1"],
        },
        repartition=repartition_nparts,
    )
    daft_df = daft_df.select(daft_df["id"].cast(DataType.int64()), daft_df["values"]).distinct()

    expected = {
        "id": [None, None, None],
        "values": ["a1", "b1", "c1"],
    }
    assert sort_arrow_table(pa.Table.from_pydict(daft_df.to_pydict()), "values") == sort_arrow_table(
        pa.Table.from_pydict(expected), "values"
    )


@pytest.mark.parametrize("repartition_nparts", [1, 2])
def test_distinct_with_empty(make_df, repartition_nparts):
    daft_df = make_df(
        {
            "id": [1],
            "values": ["a1"],
        },
        repartition=repartition_nparts,
    )
    daft_df = daft_df.where(daft_df["id"] != 1).distinct()
    daft_df.collect()

    resultset = daft_df.to_pydict()
    assert len(resultset["id"]) == 0
    assert len(resultset["values"]) == 0
