import numpy as np
from icecream import ic
from utils.excel_utils import convert_coor_to_cell_string
# Get correction results
def get_correction_results(old_rows, new_rows):
    # ic(new_rows)
    # ic(np.where(old_rows != new_rows))
    x_coordinates, y_coordinates = np.where(old_rows != new_rows)
    cell_coordinates = [(int(x), int(y)) for x, y in zip(x_coordinates, y_coordinates)]

    # Return old_value, new_value, coordinate
    return [
        {
            "old_value": old_rows[x][y],
            "new_value": new_rows[x][y],
            "coordinates": (x, y),
            "cell": convert_coor_to_cell_string(x, y)
        }
        for x, y in cell_coordinates
        if str(old_rows[x][y]).strip() != str(new_rows[x][y]).strip()
    ]