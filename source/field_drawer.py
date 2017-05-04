from PIL import Image, ImageDraw
from io import BytesIO


class FieldDrawer:
    def __init__(self, field_size, field):
        self.field_size = field_size
        self.field = field

    def img(self, cell_size=50, border_width=1, x_width=1, o_width=1, won_width=5,
            border_color="#000000", bg_color="#ffffff", text_color="#000000",
            last_x_color="#ff0000", last_o_color="#0000FF", default_cell_color="#000000"):
        width = cell_size * (self.field_size + 1) + border_width * self.field_size
        size = (width, width)
        image = Image.new("RGB", size, bg_color)
        draw = ImageDraw.Draw(image)

        for x in range(self.field_size):
            x_pos = cell_size * (x + 1) + border_width * x
            draw.line([x_pos, 0, x_pos, width - 1], width=border_width,
                      fill=border_color)
        for y in range(self.field_size):
            y_pos = cell_size * (y + 1) + border_width * y
            draw.line([0, y_pos, width - 1, y_pos], width=border_width,
                      fill=border_color)

        # for x in range(self.field_size):
        #     for y in range(self.field_size):
        #         x_low = (cell_size + border_width) * (x + 1)
        #         x_high = x_low + cell_size - 1
        #         y_low = (cell_size + border_width) * (y + 1)
        #         y_high = y_low + cell_size - 1
        #         if self[self.xy(x, y)] == 'x':
        #             if (x, y) == self.last_x:
        #                 color = last_x_color
        #             else:
        #                 color = default_cell_color
        #             draw.line([x_low, y_low, x_high, y_high], width=x_width, fill=color)
        #             draw.line([x_low, y_high, x_high, y_low], width=x_width, fill=color)
        #         elif self[self.xy(x, y)] == 'o':
        #             if (x, y) == self.last_o:
        #                 color = last_o_color
        #             else:
        #                 color = default_cell_color
        #             draw.ellipse([x_low, y_low, x_high, y_high], outline=color)
        #
        # for x in range(self.field_size):
        #     y_pos = 0
        #     x_pos = cell_size * (x + 1) + border_width * x + 5
        #     draw.text((x_pos, y_pos), str(x + 1), fill=text_color)
        #
        # for y in range(self.field_size):
        #     x_pos = 5
        #     y_pos = cell_size * (y + 1) + border_width * y
        #     draw.text((x_pos, y_pos), str(y + 1), fill=text_color)

        buffer = BytesIO()
        image.save(buffer, format="png")
        buffer.seek(0)
        return buffer
