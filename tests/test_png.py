import os
import sys

from ecoscope.mapping.map import EcoMap

sys.path.append("../ecoscope")


m = EcoMap(draw_control=False)

relative_path = os.path.join("tests/test_output/png_map.png")
m.to_png(relative_path)
