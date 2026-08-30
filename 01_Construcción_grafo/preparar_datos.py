# Importar librerias necesarias
import rasterio
import geopandas as gpd

# Parametros
PATH = r"C:\Users\Nerea\OneDrive\Escritorio\5º ING.CIVIL + MATEMÁTICAS\TFG CAMINOS"
PATH_INPUT = PATH + r"\data_nerea"
PATH_OUTPUT = PATH + r"\resultados"

EPSG = 25830 # Asignamos el sistema de referencia
dst_crs = rasterio.crs.CRS.from_epsg(EPSG)

# Carga de los archivos y shapes que se van a utilizar en este script
basin_file = r"\polygon_area_stydy.geojson"
streams_real_file = r"\trazado_barrancos.shp"
streams_artificial_file = r"\trazado_cauces_artificiales.shp"
nodes_file = r"\nodos.shp" # añado este ya que estan definidos los 
# nodos cabecera, desembocadura, confluencias tanto artificiales como naturales.
flood_file = r"\huella_inundacion_dana24.geojson"

# Leer las capas que se han cargado anteriormente
gdf_basin = gpd.read_file(PATH_INPUT + basin_file).to_crs(dst_crs)
streams_real = gpd.read_file(PATH_INPUT + streams_real_file).to_crs(dst_crs)
streams_artificial = gpd.read_file(PATH_INPUT + streams_artificial_file).to_crs(dst_crs)
nodes = gpd.read_file(PATH_INPUT + nodes_file).to_crs(dst_crs)
flooded_area = gpd.read_file(PATH_INPUT + flood_file).to_crs(dst_crs)

# Unir todas las geometrias en una sola
gdf_basin = gpd.GeoDataFrame({"geometry": [gdf_basin.union_all()]},crs=gdf_basin.crs)

streams_real['id'] = 'r_' + streams_real['id'].astype(str)
streams_artificial['id'] = 'a_' + streams_artificial['id'].astype(str)

# Join and filter streams within gdf_basin
# streams = pd.concat([streams_artificial,streams_real]) #,channels_artificial])
streams_real_basin = gpd.overlay(streams_real, gdf_basin, how="intersection")
streams_artificial_basin = gpd.overlay(streams_artificial, gdf_basin, how="intersection")
flooded_area_basin = gpd.overlay(flooded_area, gdf_basin, how="intersection")

# Guardar resultados
streams_real_basin.to_file(PATH_OUTPUT + r"\trazado_barrancos_recorte.geojson", driver="GeoJSON")
streams_artificial_basin.to_file(PATH_OUTPUT + r"\trazado_cauces_artificiales_recorte.geojson", driver="GeoJSON")
flooded_area_basin.to_file(PATH_OUTPUT + r"\huella_inundacion_recorte.geojson", driver="GeoJSON")
nodes.to_file(PATH_OUTPUT + r"\nodos.geojson", driver="GeoJSON")

# Quiero que me muestre las longitudes de las capas que he creado
print("Barrancos:", len(streams_real_basin))
print("Cauces artificiales:", len(streams_artificial_basin))
print("Nodos:", len(nodes))
print("Huella inundación:", len(flooded_area_basin))