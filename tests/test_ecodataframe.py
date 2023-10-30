import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, box

from ecoscope.base import EcoDataFrame


@pytest.fixture
def gdf():
    return gpd.GeoDataFrame(
        {
            "id": [1, 2],
            "my_geometry": [box(1, 1, 2, 2), box(3, 3, 4, 4)],
            "other_geometry": [Point(0, 0), Point(1, 1)],
        },
        geometry="my_geometry",
        crs="epsg:4326",
    )


def test_constructor():
    edf = EcoDataFrame(gdf)
    assert isinstance(edf, EcoDataFrame)
    assert edf._constructor == EcoDataFrame


def test_crs_gdf(gdf):
    edf = EcoDataFrame(gdf)
    assert edf.crs == "epsg:4326"


def test_crs_custom(gdf):
    edf = gdf.copy()
    edf.crs = None
    edf = EcoDataFrame(edf, crs="epsg:3857")
    assert edf.crs == "epsg:3857"


def test_to_crs(gdf):
    edf = EcoDataFrame(gdf)
    edf = edf.to_crs("epsg:3857")
    assert isinstance(edf, EcoDataFrame)
    assert edf.crs == "epsg:3857"


def test_geometry_gdf(gdf):
    edf = EcoDataFrame(gdf)
    assert edf.geometry.name == "my_geometry"


def test_geometry_custom(gdf):
    edf = EcoDataFrame(gdf, geometry="other_geometry")
    assert edf.geometry.name == "other_geometry"


def test_set_geometry(gdf):
    edf = EcoDataFrame(gdf)
    edf = edf.set_geometry("other_geometry")
    assert isinstance(edf, EcoDataFrame)
    assert edf.geometry.name == "other_geometry"


def test_from_file(mocker):
    mock = mocker.patch.object(gpd.GeoDataFrame, "from_file")
    edf = EcoDataFrame.from_file("file_name.geojson")
    mock.assert_called_once_with("file_name.geojson")
    assert isinstance(edf, EcoDataFrame)


def test_from_features(mocker):
    mock = mocker.patch.object(gpd.GeoDataFrame, "from_features")
    edf = EcoDataFrame.from_features("__features__")
    mock.assert_called_once_with("__features__")
    assert isinstance(edf, EcoDataFrame)


def test_getitem_series(gdf):
    edf = EcoDataFrame(gdf)
    edf = edf[edf.id > 1]
    assert isinstance(edf, EcoDataFrame)
    assert len(edf) == 1


def test_getitem_list(gdf):
    edf = EcoDataFrame(gdf)
    edf = edf[["id"]]
    assert isinstance(edf, EcoDataFrame)
    assert len(edf) == 2


def test_getitem_slice(gdf):
    edf = EcoDataFrame(gdf)
    edf = edf[slice(1)]
    assert isinstance(edf, EcoDataFrame)
    assert len(edf) == 1


def test_astype():
    edf = EcoDataFrame({"a": [1], "geometry": [Point(0, 0)]})
    edf = edf.astype("object")
    assert isinstance(edf, EcoDataFrame)


def test_merge():
    edf1 = EcoDataFrame({"lkey": ["foo", "bar"], "value": [1, 2]})
    edf2 = EcoDataFrame({"rkey": ["foo", "bar"], "value": [5, 6]})
    edf = edf1.merge(edf2, left_on="lkey", right_on="rkey")
    assert isinstance(edf, EcoDataFrame)


def test_dissolve():
    edf = EcoDataFrame({"a": [1], "geometry": [Point(0, 0)]})
    edf = edf.dissolve(by="a")
    assert isinstance(edf, EcoDataFrame)


@pytest.mark.filterwarnings("ignore::FutureWarning")
def test_explode():
    edf = EcoDataFrame({"a": [1], "geometry": [Point(0, 0)]})
    edf = edf.explode()
    assert isinstance(edf, EcoDataFrame)


def test_concat():
    edf1 = EcoDataFrame({"a": [1], "geometry": [Point(0, 0)]})
    edf2 = EcoDataFrame({"a": [2], "geometry": [Point(1, 1)]})
    edf = pd.concat([edf1, edf2])
    assert isinstance(edf, EcoDataFrame)


def test_plot_series(mocker):
    series_plot_mock = mocker.patch.object(pd.Series, "plot")
    edf = EcoDataFrame({"x": [1]})
    edf["x"].plot()
    series_plot_mock.assert_called_once_with()


def test_plot_geoseries(mocker):
    geoseries_plot_mock = mocker.patch.object(gpd.GeoSeries, "plot")
    edf = EcoDataFrame({"geometry": [Point(0, 0)]})
    edf["geometry"].plot()
    geoseries_plot_mock.assert_called_once_with()


def test_plot_dataframe(mocker):
    dataframe_plot_mock = mocker.patch.object(pd.DataFrame, "plot")
    edf = EcoDataFrame({"x": [1], "y": [1]})
    edf[["x", "y"]].plot()
    dataframe_plot_mock.assert_called_once_with()


def test_plot_geodataframe(mocker):
    geodataframe_plot_mock = mocker.patch.object(gpd.GeoDataFrame, "plot")
    edf = EcoDataFrame({"x": [1], "geometry": [Point(0, 0)]})
    subset = edf[["x", "geometry"]]
    subset.plot(column="x")
    geodataframe_plot_mock.assert_called_once_with(subset, column="x")
