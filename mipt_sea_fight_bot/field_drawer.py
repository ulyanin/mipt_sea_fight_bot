from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


class FieldDrawer:
    def __init__(self, field_size, user_board, user_board_stricken, user_board_hidden,
                 bot_board, bot_board_stricken, bot_board_hidden):
        self.bot_board_hidden = bot_board_hidden
        self.user_board_hidden = user_board_hidden
        self.field_size = field_size
        self.user_board = user_board
        self.user_board_stricken = user_board_stricken
        self.bot_board = bot_board
        self.bot_board_stricken = bot_board_stricken

    def img(self, cell_size=50, border_width=1, ship_border_width=2, x_width=3, xo_color="#ff0000",
            border_color="#000000", bg_color="#ffffff", text_color="#000000", hidden_color="#636363",
            ship_border_color="#200772", ship_fill_color="#0000ff",
            last_x_color="#ff0000", last_o_color="#0000FF", default_cell_color="#000000"):
        width = cell_size * (2 * self.field_size + 2) + 2 * border_width * self.field_size
        height = cell_size * (self.field_size + 1) + border_width * self.field_size
        size = (width, height)
        image = Image.new("RGB", size, bg_color)
        draw = ImageDraw.Draw(image)
        offset = cell_size // 5
        font = ImageFont.truetype("DejaVuSansMono.ttf", cell_size - 2 * offset)
        for i in range(self.field_size):
            # vertical
            draw.text((offset, offset + (i + 1) * (cell_size + border_width)),
                      str(i), text_color, font=font)
            draw.text((offset + (cell_size + border_width) * (self.field_size + 1),
                       offset + (i + 1) * (cell_size + border_width)),
                      str(i), text_color, font=font)
            # horizontal
            draw.text((offset + (i + 1) * (cell_size + border_width), offset),
                      chr(ord('A') + i), text_color, font=font)
            draw.text((offset + (2 + i + self.field_size) * (cell_size + border_width), offset),
                      chr(ord('A') + i), text_color, font=font)
        # horizontal: vertical lines
        for x in range(self.field_size * 2 + 1):
            x_pos = cell_size * (x + 1) + border_width * x
            draw.line([x_pos, 0, x_pos, height - 1], width=border_width,
                      fill=border_color)
        x_pos = cell_size * (self.field_size + 1) + border_width * self.field_size
        draw.line([x_pos, 0, x_pos, height - 1], width=border_width,
                  fill=(255, 0, 0))
        # vertical
        for y in range(self.field_size):
            y_pos = cell_size * (y + 1) + border_width * y
            draw.line([0, y_pos, width - 1, y_pos], width=border_width,
                      fill=border_color)

        # self.user_board_stricken[2][2] = 1
        # self.user_board_stricken[2][3] = 1
        # self.bot_board_stricken = [[1] * self.field_size for _ in range(self.field_size)]

        # draw ships
        for x in range(self.field_size):
            for y in range(self.field_size):
                # if have a ship
                if self.user_board[x][y]:
                    x_end_pos = x
                    y_end_pos = y
                    while x_end_pos < self.field_size and self.user_board[x_end_pos][y]:
                        x_end_pos += 1
                    while y_end_pos < self.field_size and self.user_board[x][y_end_pos]:
                        y_end_pos += 1
                    draw.rectangle([cell_size * (t + 1) + border_width * t
                                    for t in [x, y, x_end_pos, y_end_pos]],
                                   fill=ship_fill_color)
                    draw.rectangle([cell_size * (t + 1) + border_width * t
                                    for t in [x, y, x_end_pos, y_end_pos]],
                                   outline=ship_border_color)
                # user board
                x_low = (cell_size + border_width) * (x + 1)
                x_high = x_low + cell_size - 1
                y_low = (cell_size + border_width) * (y + 1)
                y_high = y_low + cell_size - 1
                if self.user_board_stricken[x][y] and self.user_board[x][y]:
                    draw.line([x_low, y_low, x_high, y_high], width=x_width, fill=xo_color)
                    draw.line([x_low, y_high, x_high, y_low], width=x_width, fill=xo_color)
                if self.user_board_hidden[x][y] and not self.user_board[x][y]:
                    if self.user_board_stricken[x][y]:
                        draw.ellipse([x_low + offset, y_low + offset,
                                      x_high - offset, y_high - offset], fill=xo_color)
                    else:
                        draw.ellipse([x_low + offset, y_low + offset,
                                      x_high - offset, y_high - offset], fill=hidden_color)
                # bot board
                x_low = (cell_size + border_width) * (x + self.field_size + 2)
                x_high = x_low + cell_size - 1
                y_low = (cell_size + border_width) * (y + 1)
                y_high = y_low + cell_size - 1
                if self.bot_board_stricken[x][y] and self.bot_board[x][y]:
                    draw.line([x_low, y_low, x_high, y_high], width=x_width, fill=xo_color)
                    draw.line([x_low, y_high, x_high, y_low], width=x_width, fill=xo_color)
                if self.bot_board_hidden[x][y] and not self.bot_board[x][y]:
                    if self.bot_board_stricken[x][y]:
                        draw.ellipse([x_low + offset, y_low + offset,
                                      x_high - offset, y_high - offset], fill=xo_color)
                    else:
                        draw.ellipse([x_low + offset, y_low + offset,
                                      x_high - offset, y_high - offset], fill=hidden_color)

                # if self.user_board[x][y]:
                #     for i in range(2):
                #         x_pos = cell_size * (x + 1) + border_width * x
                #         y_pos = cell_size * (y + 1) + border_width * y
                #         # vertical
                #         draw.line([x_pos, y_pos + cell_size * i,
                #                    x_pos + cell_size, y_pos + cell_size * i],
                #                   width=ship_border_width,
                #                   fill=ship_border_color)
                #         # horizontal
                #         draw.line([x_pos + cell_size * i, y_pos,
                #                    x_pos + cell_size * i, y_pos + cell_size],
                #                   width=ship_border_width,
                #                   fill=ship_border_color)

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
