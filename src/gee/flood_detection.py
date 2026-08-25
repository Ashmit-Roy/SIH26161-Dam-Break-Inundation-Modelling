import ee

def init_gee(project_id="sih-dam-break"):
    try:
        ee.Initialize(project=project_id)
        print("Google Earth Engine initialized successfully!")
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=project_id)
        print("Google Earth Engine authenticated and initialized successfully!")

def get_sar_composite(aoi, start_date, end_date):
    """Fetches Sentinel-1 IW SAR median composite (speckle filtered)."""
    return (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
        .select("VV")
        .median()
    )

def extract_flood_extent(aoi, pre_dates, post_dates, threshold_db=-17.0):
    """Computes flood extent: Water NOW that was NOT permanent water before."""
    pre_sar = get_sar_composite(aoi, pre_dates[0], pre_dates[1])
    post_sar = get_sar_composite(aoi, post_dates[0], post_dates[1])

    pre_water = pre_sar.lt(threshold_db)
    post_water = post_sar.lt(threshold_db)

    # Isolated new flood extent
    new_flood = post_water.And(pre_water.Not()).rename("flood_extent")
    
    # Calculate area (m2)
    area_img = new_flood.multiply(ee.Image.pixelArea())
    stats = area_img.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=aoi,
        scale=10,
        maxPixels=1e9
    )
    return new_flood, stats
