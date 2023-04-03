import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from cartopy.feature import ShapelyFeature
import matplotlib.patches as mpatches
import geopandas as gpd
import cartopy.crs as ccrs

# ---------------------------------------------------------------------------------------------------------------------
# in this section, write the script to load the data and complete the main part of the analysis.
# try to print the results to the screen using the format method demonstrated in the workbook

# load the necessary data here and transform to a UTM projection
# load Data Files
counties = gpd.read_file('data_files/Counties.shp')
wards = gpd.read_file('data_files/NI_Wards.shp')

# target crs to use
myCRS = ccrs.UTM(29)

# transform to UTM projection
counties_utm = counties.to_crs(myCRS)
wards_utm = wards.to_crs(myCRS)

# set up the plot axes and plot the county polygon (boundary only)
ax=counties_utm.plot(fc='none')

#create a new gpd which is a copy of wards_utm so that that my original gpd remains unchanged
wards_reppoint = wards_utm.copy()

#create representative points for the ward polygons and plot on existing axes
wards_reppoint['geometry'] = wards_reppoint['geometry'].representative_point()
wards_reppoint.plot(ax=ax)

#perform a spatial join on counties_item and wards_reppoint
join = gpd.sjoin(counties_utm, wards_reppoint, how='inner', lsuffix='left', rsuffix='right')
join.shape

join_sum_county = join.groupby(['CountyName'])['Population'].sum()
join_sum_ward = join.groupby(['CountyName','Ward'])['Population'].sum()
print(join_sum_county)
print(join_sum_ward)

# create a figure of size 10x10 (representing the page size in inches
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))

# add gridlines below
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.right_labels = False
gridlines.bottom_labels = False

# to make a nice colorbar that stays in line with our map, use these lines:
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1, axes_class=plt.Axes)

# plot the ward data into our axis, using
ward_plot = wards_utm.plot(column='Population', ax=ax, vmin=1000, vmax=8000, cmap='viridis',
                       legend=True, cax=cax, legend_kwds={'label': 'Resident Population'})

county_outlines = ShapelyFeature(counties_utm['geometry'], myCRS, edgecolor='r', facecolor='none')

ax.add_feature(county_outlines)
county_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='r')]

ax.legend(county_handles, ['County Boundaries'], fontsize=12, loc='upper left', framealpha=1)

# save the figure
fig.savefig('sample_map.png', dpi=300, bbox_inches='tight')