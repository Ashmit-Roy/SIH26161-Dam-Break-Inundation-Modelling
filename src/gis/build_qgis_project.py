"""
QGIS Project Generator for SIH26161 Dam Break Inundation Modelling.

Constructs a valid QGIS project XML (.qgs) referencing the preprocessed DEM,
hillshade, vector layers (Dams, Rivers, Study Area, Infrastructure), and
Dam-break simulation results (Flood Depth, Inundation Extent, Hazard Zones).
Packs the project into `qgis/dam_break.qgz` with clean relative paths.
"""

import uuid
import zipfile
from pathlib import Path


def build_qgis_project(workspace_root: Path) -> Path:
    qgis_dir = workspace_root / "qgis"
    qgis_dir.mkdir(parents=True, exist_ok=True)

    qgs_path = qgis_dir / "dam_break.qgs"
    qgz_path = qgis_dir / "dam_break.qgz"

    # Layer UUIDs
    id_dams = f"dam_locations_{uuid.uuid4().hex[:8]}"
    id_infra = f"critical_infra_{uuid.uuid4().hex[:8]}"
    id_sph_sat = f"sph_sat_overlay_{uuid.uuid4().hex[:8]}"
    id_delft_roads = f"delft_roads_{uuid.uuid4().hex[:8]}"
    id_delft_bridges = f"delft_bridges_{uuid.uuid4().hex[:8]}"
    id_river = f"river_reach_{uuid.uuid4().hex[:8]}"
    id_boundary = f"study_boundary_{uuid.uuid4().hex[:8]}"
    id_flood_ext = f"flood_extent_{uuid.uuid4().hex[:8]}"
    id_hazard = f"hazard_zones_{uuid.uuid4().hex[:8]}"
    id_depth = f"flood_depth_{uuid.uuid4().hex[:8]}"
    id_velocity = f"flow_velocity_{uuid.uuid4().hex[:8]}"
    id_hillshade = f"hillshade_{uuid.uuid4().hex[:8]}"
    id_dem = f"dem_{uuid.uuid4().hex[:8]}"

    qgs_xml = f"""<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.0-Prizren" projectname="SIH26161 - Rishi Ganga Dam Break Inundation Modelling">
  <homePath path=".."/>
  <title>SIH26161 - Rishi Ganga Dam Break Inundation Study</title>
  <projectCrs>
    <spatialrefsys nativeFormat="Wkt">
      <wkt>PROJCRS["WGS 84 / UTM zone 44N",BASEGEOGCRS["WGS 84",DATUM["World Geodetic System 1984",ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],ID["EPSG",4326]],CONVERSION["UTM zone 44N",METHOD["Transverse Mercator",ID["EPSG",9807]],PARAMETER["Latitude of natural origin",0,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8801]],PARAMETER["Longitude of natural origin",81,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8802]],PARAMETER["Scale factor at natural origin",0.9996,SCALEUNIT["unity",1],ID["EPSG",8805]],PARAMETER["False easting",500000,LENGTHUNIT["metre",1],ID["EPSG",8806]],PARAMETER["False northing",0,LENGTHUNIT["metre",1],ID["EPSG",8807]]],CS[Cartesian,2],AXIS["(E)",east,ORDER[1],LENGTHUNIT["metre",1]],AXIS["(N)",north,ORDER[2],LENGTHUNIT["metre",1]],USAGE[SCOPE["Engineering survey, topographic mapping."],AREA["Between 78°E and 84°E, northern hemisphere."],BBOX[0,78,84,84]],ID["EPSG",32644]]</wkt>
      <proj4>+proj=utm +zone=44 +datum=WGS84 +units=m +no_defs</proj4>
      <srsid>3128</srsid>
      <srid>32644</srid>
      <authid>EPSG:32644</authid>
      <description>WGS 84 / UTM zone 44N</description>
      <projectionacronym>utm</projectionacronym>
      <ellipsoidacronym>EPSG:7030</ellipsoidacronym>
      <geographicflag>false</geographicflag>
    </spatialrefsys>
  </projectCrs>
  
  <layer-tree-group>
    <customproperties>
      <Option/>
    </customproperties>
    <custom-order enabled="0"/>
    
    <layer-tree-group name="Dam Break Simulation Results" expanded="1" checked="Qt::Checked">
      <layer-tree-layer name="Dam Locations" id="{id_dams}" checked="Qt::Checked"/>
      <layer-tree-layer name="Critical Infrastructure" id="{id_infra}" checked="Qt::Checked"/>
      <layer-tree-layer name="Impacted Bridges" id="{id_delft_bridges}" checked="Qt::Checked"/>
      <layer-tree-layer name="Inundated Roads &amp; Highway" id="{id_delft_roads}" checked="Qt::Checked"/>
      <layer-tree-layer name="SPH vs Satellite Hazard Overlay" id="{id_sph_sat}" checked="Qt::Checked"/>
      <layer-tree-layer name="Flood Inundation Extent" id="{id_flood_ext}" checked="Qt::Checked"/>
      <layer-tree-layer name="Flood Hazard Zones" id="{id_hazard}" checked="Qt::Unchecked"/>
      <layer-tree-layer name="Peak Flood Depth (m)" id="{id_depth}" checked="Qt::Checked"/>
      <layer-tree-layer name="Max Flow Velocity (m/s)" id="{id_velocity}" checked="Qt::Unchecked"/>
    </layer-tree-group>
    
    <layer-tree-group name="Hydrology &amp; Basework" expanded="1" checked="Qt::Checked">
      <layer-tree-layer name="River Reach Centerline" id="{id_river}" checked="Qt::Checked"/>
      <layer-tree-layer name="Study Area Basin Boundary" id="{id_boundary}" checked="Qt::Checked"/>
    </layer-tree-group>
    
    <layer-tree-group name="Terrain &amp; Elevation" expanded="1" checked="Qt::Checked">
      <layer-tree-layer name="Terrain Hillshade" id="{id_hillshade}" checked="Qt::Checked"/>
      <layer-tree-layer name="Rishi Ganga DEM (30m)" id="{id_dem}" checked="Qt::Unchecked"/>
    </layer-tree-group>
  </layer-tree-group>
  
  <projectlayers>
    <!-- Vector: Dam Locations -->
    <maplayer type="vector" id="{id_dams}" name="Dam Locations" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories">
      <datasource>./data/vector/dam_locations.geojson</datasource>
      <layername>Dam Locations</layername>
      <srs>
        <spatialrefsys nativeFormat="Wkt">
          <authid>EPSG:4326</authid>
          <description>WGS 84</description>
        </spatialrefsys>
      </srs>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="marker" name="0" alpha="1" clip_to_extent="1">
            <layer class="SimpleMarker" enabled="1" locked="0">
              <Option type="Map">
                <Option name="color" type="QString" value="230,20,20,255"/>
                <Option name="outline_color" type="QString" value="255,255,255,255"/>
                <Option name="outline_width" type="QString" value="0.8"/>
                <Option name="size" type="QString" value="5.5"/>
                <Option name="name" type="QString" value="diamond"/>
              </Option>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>
    
    <!-- Vector: Critical Infrastructure -->
    <maplayer type="vector" id="{id_infra}" name="Critical Infrastructure" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories">
      <datasource>./data/vector/critical_infrastructure.geojson</datasource>
      <layername>Critical Infrastructure</layername>
      <srs>
        <spatialrefsys nativeFormat="Wkt">
          <authid>EPSG:4326</authid>
          <description>WGS 84</description>
        </spatialrefsys>
      </srs>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="marker" name="0" alpha="1" clip_to_extent="1">
            <layer class="SimpleMarker" enabled="1" locked="0">
              <Option type="Map">
                <Option name="color" type="QString" value="255,140,0,255"/>
                <Option name="outline_color" type="QString" value="0,0,0,255"/>
                <Option name="outline_width" type="QString" value="0.5"/>
                <Option name="size" type="QString" value="4.0"/>
                <Option name="name" type="QString" value="triangle"/>
              </Option>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>

    <!-- Vector: Delft3D Damaged Bridges -->
    <maplayer type="vector" id="{id_delft_bridges}" name="Impacted Bridges" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories">
      <datasource>./outputs/delft3d_damaged_bridges.geojson</datasource>
      <layername>Impacted Bridges</layername>
      <srs>
        <spatialrefsys nativeFormat="Wkt">
          <authid>EPSG:4326</authid>
          <description>WGS 84</description>
        </spatialrefsys>
      </srs>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="marker" name="0" alpha="1" clip_to_extent="1">
            <layer class="SimpleMarker" enabled="1" locked="0">
              <Option type="Map">
                <Option name="color" type="QString" value="220,20,60,255"/>
                <Option name="outline_color" type="QString" value="255,255,255,255"/>
                <Option name="outline_width" type="QString" value="0.8"/>
                <Option name="size" type="QString" value="5.0"/>
                <Option name="name" type="QString" value="cross2"/>
              </Option>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>

    <!-- Vector: Delft3D Inundated Roads -->
    <maplayer type="vector" id="{id_delft_roads}" name="Inundated Roads &amp; Highway" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories">
      <datasource>./outputs/delft3d_damaged_roads.geojson</datasource>
      <layername>Inundated Roads &amp; Highway</layername>
      <srs>
        <spatialrefsys nativeFormat="Wkt">
          <authid>EPSG:4326</authid>
          <description>WGS 84</description>
        </spatialrefsys>
      </srs>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="line" name="0" alpha="1" clip_to_extent="1">
            <layer class="SimpleLine" enabled="1" locked="0">
              <Option type="Map">
                <Option name="line_color" type="QString" value="230,50,50,255"/>
                <Option name="line_width" type="QString" value="1.8"/>
              </Option>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>

    <!-- Vector: River Reach -->
    <maplayer type="vector" id="{id_river}" name="River Reach Centerline" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories">
      <datasource>./data/vector/river_centerline.geojson</datasource>
      <layername>River Reach Centerline</layername>
      <srs>
        <spatialrefsys nativeFormat="Wkt">
          <authid>EPSG:4326</authid>
          <description>WGS 84</description>
        </spatialrefsys>
      </srs>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="line" name="0" alpha="1" clip_to_extent="1">
            <layer class="SimpleLine" enabled="1" locked="0">
              <Option type="Map">
                <Option name="line_color" type="QString" value="20,100,220,255"/>
                <Option name="line_width" type="QString" value="1.2"/>
              </Option>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>

    <!-- Vector: Basin Boundary -->
    <maplayer type="vector" id="{id_boundary}" name="Study Area Basin Boundary" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories">
      <datasource>./data/vector/study_area_boundary.geojson</datasource>
      <layername>Study Area Basin Boundary</layername>
      <srs>
        <spatialrefsys nativeFormat="Wkt">
          <authid>EPSG:4326</authid>
          <description>WGS 84</description>
        </spatialrefsys>
      </srs>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="fill" name="0" alpha="1" clip_to_extent="1">
            <layer class="SimpleLine" enabled="1" locked="0">
              <Option type="Map">
                <Option name="line_color" type="QString" value="40,40,40,255"/>
                <Option name="line_style" type="QString" value="dash"/>
                <Option name="line_width" type="QString" value="0.8"/>
              </Option>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>

    <!-- Vector: SPH vs Satellite Hazard Overlay -->
    <maplayer type="vector" id="{id_sph_sat}" name="SPH vs Satellite Hazard Overlay" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories">
      <datasource>./outputs/sph_satellite_overlay.geojson</datasource>
      <layername>SPH vs Satellite Hazard Overlay</layername>
      <srs>
        <spatialrefsys nativeFormat="Wkt">
          <authid>EPSG:4326</authid>
          <description>WGS 84</description>
        </spatialrefsys>
      </srs>
      <renderer-v2 type="categorizedSymbol" attr="category_code" symbollevels="0">
        <categories>
          <category value="1" label="Agreement (Simulated &amp; Observed)" symbol="0"/>
          <category value="2" label="SPH Simulated Only" symbol="1"/>
          <category value="3" label="Satellite Observed Only" symbol="2"/>
        </categories>
        <symbols>
          <symbol type="fill" name="0" alpha="0.75"><layer class="SimpleFill"><Option type="Map"><Option name="color" type="QString" value="0,208,255,190"/><Option name="outline_color" type="QString" value="0,136,204,255"/></Option></layer></symbol>
          <symbol type="fill" name="1" alpha="0.65"><layer class="SimpleFill"><Option type="Map"><Option name="color" type="QString" value="255,153,0,165"/><Option name="outline_color" type="QString" value="204,102,0,255"/></Option></layer></symbol>
          <symbol type="fill" name="2" alpha="0.65"><layer class="SimpleFill"><Option type="Map"><Option name="color" type="QString" value="255,51,102,165"/><Option name="outline_color" type="QString" value="179,0,45,255"/></Option></layer></symbol>
        </symbols>
      </renderer-v2>
    </maplayer>

    <!-- Vector: Flood Extent -->
    <maplayer type="vector" id="{id_flood_ext}" name="Flood Inundation Extent" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories">
      <datasource>./outputs/flood_extent.geojson</datasource>
      <layername>Flood Inundation Extent</layername>
      <srs>
        <spatialrefsys nativeFormat="Wkt">
          <authid>EPSG:4326</authid>
          <description>WGS 84</description>
        </spatialrefsys>
      </srs>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="fill" name="0" alpha="0.65" clip_to_extent="1">
            <layer class="SimpleFill" enabled="1" locked="0">
              <Option type="Map">
                <Option name="color" type="QString" value="0,170,255,165"/>
                <Option name="outline_color" type="QString" value="0,90,190,255"/>
                <Option name="outline_width" type="QString" value="0.5"/>
              </Option>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>

    <!-- Vector: Hazard Zones -->
    <maplayer type="vector" id="{id_hazard}" name="Flood Hazard Zones" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories">
      <datasource>./outputs/hazard_zones.geojson</datasource>
      <layername>Flood Hazard Zones</layername>
      <srs>
        <spatialrefsys nativeFormat="Wkt">
          <authid>EPSG:4326</authid>
          <description>WGS 84</description>
        </spatialrefsys>
      </srs>
      <renderer-v2 type="categorizedSymbol" attr="hazard_code" symbollevels="0">
        <categories>
          <category value="1" label="Low Hazard (Caution)" symbol="0"/>
          <category value="2" label="Moderate Hazard" symbol="1"/>
          <category value="3" label="Significant Hazard" symbol="2"/>
          <category value="4" label="Extreme Hazard" symbol="3"/>
        </categories>
        <symbols>
          <symbol type="fill" name="0" alpha="0.6"><layer class="SimpleFill"><Option type="Map"><Option name="color" type="QString" value="255,255,100,160"/><Option name="outline_color" type="QString" value="180,180,0,255"/></Option></layer></symbol>
          <symbol type="fill" name="1" alpha="0.6"><layer class="SimpleFill"><Option type="Map"><Option name="color" type="QString" value="255,165,0,160"/><Option name="outline_color" type="QString" value="200,100,0,255"/></Option></layer></symbol>
          <symbol type="fill" name="2" alpha="0.6"><layer class="SimpleFill"><Option type="Map"><Option name="color" type="QString" value="255,50,50,160"/><Option name="outline_color" type="QString" value="180,0,0,255"/></Option></layer></symbol>
          <symbol type="fill" name="3" alpha="0.7"><layer class="SimpleFill"><Option type="Map"><Option name="color" type="QString" value="150,0,100,180"/><Option name="outline_color" type="QString" value="90,0,50,255"/></Option></layer></symbol>
        </symbols>
      </renderer-v2>
    </maplayer>

    <!-- Raster: Flood Depth -->
    <maplayer type="raster" id="{id_depth}" name="Peak Flood Depth (m)" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories" autoRefreshMode="Disabled">
      <datasource>./outputs/flood_depth.tif</datasource>
      <layername>Peak Flood Depth (m)</layername>
      <srs>
        <spatialrefsys nativeFormat="Wkt">
          <authid>EPSG:32644</authid>
          <description>WGS 84 / UTM zone 44N</description>
        </spatialrefsys>
      </srs>
      <pipe-data>
        <rasterrenderer type="singlebandpseudocolor" band="1" opacity="0.8" classificationMin="0.2" classificationMax="15.0">
          <rastershader>
            <colorrampshader colorRampType="INTERPOLATED" clip="0">
              <item color="#e0f3f8" label="0.2 m" value="0.2"/>
              <item color="#91bfdb" label="3.0 m" value="3.0"/>
              <item color="#4575b4" label="8.0 m" value="8.0"/>
              <item color="#313695" label="15.0+ m" value="15.0"/>
            </colorrampshader>
          </rastershader>
        </rasterrenderer>
      </pipe-data>
    </maplayer>

    <!-- Raster: Flow Velocity -->
    <maplayer type="raster" id="{id_velocity}" name="Max Flow Velocity (m/s)" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories" autoRefreshMode="Disabled">
      <datasource>./outputs/flow_velocity.tif</datasource>
      <layername>Max Flow Velocity (m/s)</layername>
      <srs>
        <spatialrefsys nativeFormat="Wkt">
          <authid>EPSG:32644</authid>
          <description>WGS 84 / UTM zone 44N</description>
        </spatialrefsys>
      </srs>
      <pipe-data>
        <rasterrenderer type="singlebandpseudocolor" band="1" opacity="0.75" classificationMin="0.5" classificationMax="16.0">
          <rastershader>
            <colorrampshader colorRampType="INTERPOLATED" clip="0">
              <item color="#fee08b" label="0.5 m/s" value="0.5"/>
              <item color="#fdae61" label="5.0 m/s" value="5.0"/>
              <item color="#f46d43" label="10.0 m/s" value="10.0"/>
              <item color="#d73027" label="16.0+ m/s" value="16.0"/>
            </colorrampshader>
          </rastershader>
        </rasterrenderer>
      </pipe-data>
    </maplayer>

    <!-- Raster: Hillshade -->
    <maplayer type="raster" id="{id_hillshade}" name="Terrain Hillshade" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories" autoRefreshMode="Disabled">
      <datasource>./outputs/terrain_hillshade.tif</datasource>
      <layername>Terrain Hillshade</layername>
      <srs>
        <spatialrefsys nativeFormat="Wkt">
          <authid>EPSG:32644</authid>
          <description>WGS 84 / UTM zone 44N</description>
        </spatialrefsys>
      </srs>
      <pipe-data>
        <rasterrenderer type="singlebandgray" grayMode="0" band="1" opacity="0.85">
          <contrastEnhancement>
            <minValue>0</minValue>
            <maxValue>255</maxValue>
            <algorithm>StretchToMinimumMaximum</algorithm>
          </contrastEnhancement>
        </rasterrenderer>
      </pipe-data>
    </maplayer>

    <!-- Raster: DEM -->
    <maplayer type="raster" id="{id_dem}" name="Rishi Ganga DEM (30m)" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories" autoRefreshMode="Disabled">
      <datasource>./data/dem/rishi_ganga_dem_30m.tif</datasource>
      <layername>Rishi Ganga DEM (30m)</layername>
      <srs>
        <spatialrefsys nativeFormat="Wkt">
          <authid>EPSG:32644</authid>
          <description>WGS 84 / UTM zone 44N</description>
        </spatialrefsys>
      </srs>
      <pipe-data>
        <rasterrenderer type="singlebandpseudocolor" band="1" opacity="1.0" classificationMin="1400" classificationMax="3800">
          <rastershader>
            <colorrampshader colorRampType="INTERPOLATED" clip="0">
              <item color="#1a9641" label="1400 m" value="1400"/>
              <item color="#a6d96a" label="2000 m" value="2000"/>
              <item color="#ffffbf" label="2600 m" value="2600"/>
              <item color="#fdae61" label="3200 m" value="3200"/>
              <item color="#d7191c" label="3800 m" value="3800"/>
            </colorrampshader>
          </rastershader>
        </rasterrenderer>
      </pipe-data>
    </maplayer>
  </projectlayers>
  
  <layerorder>
    <layer id="{id_dams}"/>
    <layer id="{id_infra}"/>
    <layer id="{id_delft_bridges}"/>
    <layer id="{id_delft_roads}"/>
    <layer id="{id_sph_sat}"/>
    <layer id="{id_river}"/>
    <layer id="{id_boundary}"/>
    <layer id="{id_flood_ext}"/>
    <layer id="{id_hazard}"/>
    <layer id="{id_depth}"/>
    <layer id="{id_velocity}"/>
    <layer id="{id_hillshade}"/>
    <layer id="{id_dem}"/>
  </layerorder>
  
  <properties>
    <Measurement>
      <DistanceUnits type="QString">meters</DistanceUnits>
      <AreaUnits type="QString">m2</AreaUnits>
    </Measurement>
    <Paths>
      <Absolute type="bool">false</Absolute>
    </Paths>
  </properties>
</qgis>
"""
    # Write .qgs
    with open(qgs_path, "w", encoding="utf-8") as f:
        f.write(qgs_xml)

    # Write .qgz (zip container containing dam_break.qgs)
    with zipfile.ZipFile(qgz_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(qgs_path, arcname="dam_break.qgs")

    print(f"Generated QGIS project: {qgs_path} and {qgz_path}")
    return qgz_path


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent
    build_qgis_project(root)
