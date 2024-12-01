import pymupdf as fitz
import logging


def path_to_shapes(new_page, paths, color, opacity=0.5):
    for path in paths:
        shape = new_page.new_shape()
        for item in path["items"]:
            if item:
                item_type = item[0]
                if item_type == "l":  # Line
                    shape.draw_line(item[1], item[2])
                elif item_type == "c":  # Curve
                    shape.draw_bezier(item[1], item[2], item[3], item[4])
                elif item_type == "qu":  # quad
                    shape.draw_quad(item[1])
                else:
                    logger = logging.getLogger(__name__)
                    logger.setLevel(logging.DEBUG)
                    logger.info("Unknown Shape: ", item)

        shape.finish(
            fill=path["fill"],  # fill color
            color=color,  # line color
            dashes=path["dashes"],  # line dashing
            even_odd=False,  # path.get("even_odd", False),  # control color of overlaps
            closePath=path["closePath"],  # whether to connect last and first point
            lineJoin=path["lineJoin"] if path["lineJoin"] else 0,  # how line joins should look like
            lineCap=max(path["lineCap"]) if path["lineCap"] else 0,  # how line ends should look like
            width=path["width"] * 2 if path["width"] else 1,  # line width
            # rect=path["rect"],
            stroke_opacity=opacity,  # same value for both
            fill_opacity=opacity,  # opacity parameters
        )
        shape.commit()
