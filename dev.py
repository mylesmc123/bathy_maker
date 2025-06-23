# %%
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np

# %%
# Load the original contour shapefile
input_shapefile = r"\\garverinc.local\gdata\Projects\2022\22T10600 - Camden Lake H-H Analysis\Design\Calculations\Hydraulics\Supplemental Agreement #3\RAS\Features\contour_253.6_str5_lake_polygon.shp"  # <-- Replace with your local path
gdf = gpd.read_file(input_shapefile)

# Get the base feature and geometry
base_geom = gdf.geometry.iloc[0]

# Elevation-area table (acres)
elevation_area = {
    240: 0.00, 241: 47.59, 242: 95.19, 243: 142.78, 244: 190.37,
    245: 237.96, 246: 285.56, 247: 333.15, 248: 380.74,
    249: 428.34, 250: 476.09, 251: 523.85, 252: 571.59, 253: 619.00
}

# %%
# Function to find buffer distance that matches target area
def find_buffer_distance(target_area, geom, tolerance=1.0):
    low, high = 0, 500  # meters
    while high - low > 0.1:
        mid = (low + high) / 2
        buffered = geom.buffer(-mid)
        if buffered.is_empty:
            high = mid
            continue
        area = buffered.area * 0.000247105  # m² to acres
        if area > target_area + tolerance:
            low = mid
        elif area < target_area - tolerance:
            high = mid
        else:
            return mid
    return mid

# %%
# Generate ring-shaped contours
features = []
current_geom = base_geom
sorted_elevations = sorted(elevation_area.items(), reverse=True)

for i in range(len(sorted_elevations) - 1):
    elev_outer, area_outer = sorted_elevations[i]
    elev_inner, area_inner = sorted_elevations[i + 1]

    if area_inner == 0:
        continue

    buffer_dist = find_buffer_distance(area_inner, current_geom)
    inner_geom = current_geom.buffer(-buffer_dist)
    if inner_geom.is_empty:
        continue

    ring_geom = current_geom.difference(inner_geom)
    features.append({'geometry': ring_geom, 'ELEV': elev_inner})
    current_geom = inner_geom

# %%
# Create GeoDataFrame
contours_gdf = gpd.GeoDataFrame(features, crs=gdf.crs)
contours_gdf
# %%
# Save to GeoPackage
output_path = r"C:\Users\MBMcManus\OneDrive - Garver\Documents\Work\Camden\contours4.gpkg"
contours_gdf.to_file(output_path, driver="GPKG", layer="Contours4")

print("Contours generated and saved to GeoPackage.")

# %%
# create a single esri shape file for each elevation
for elev in contours_gdf['ELEV'].unique():
    elev_gdf = contours_gdf[contours_gdf['ELEV'] == elev]
    output_shp_path = f"C:\\Users\\MBMcManus\\OneDrive - Garver\\Documents\\Work\\Camden\\contour_{elev}.shp"
    elev_gdf.to_file(output_shp_path, driver="ESRI Shapefile")
    print(f"Saved contours for elevation {elev} to {output_shp_path}")
# %%
